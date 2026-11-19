
from flask import Flask, render_template, request
import joblib
from pathlib import Path

from src.clustering import get_movies_by_cluster
from src.persistence import load_artifacts
from src.content_model import calculate_all_similarities
from src.popularity_model import (
    calculate_weighted_rating,
    normalize_weighted_ratings
)
from src.hybrid import (
    merge_recommendation_scores,
    handle_missing_ratings,
    calculate_hybrid_score,
    recommend_hybrid_movies
)


PROJECT_ROOT = Path(__file__).resolve().parent

app = Flask(__name__)


# Load clustered movies
clustered_movies = joblib.load(
    PROJECT_ROOT / "outputs" / "models" / "movies_clustered.joblib"
)


# Load recommendation artifacts once
vectorizer, tfidf_matrix, movies_catalogue = load_artifacts()


# Prepare normalized ratings once
weighted_movies = calculate_weighted_rating(movies_catalogue)
normalized_movies = normalize_weighted_ratings(weighted_movies)


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    categories = (
        clustered_movies[["cluster", "cluster_name"]]
        .drop_duplicates()
        .sort_values("cluster")
        .to_dict(orient="records")
    )

    return render_template(
        "index.html",
        categories=categories
    )


# --------------------------------------------------
# MOVIE SEARCH
# --------------------------------------------------

@app.route("/search", methods=["GET"])
def search():

    query = request.args.get("q", "").strip()
    search_results = []

    if query:
        matches = movies_catalogue[
            movies_catalogue["title"].str.contains(
                query,
                case=False,
                na=False,
                regex=False
            )
        ].head(10)

        search_results = matches[
            ["movie_id", "title", "genres", "poster_path"]
        ].to_dict(orient="records")

    return render_template(
        "search.html",
        search_results=search_results,
        query=query
    )


# --------------------------------------------------
# MOVIE RECOMMENDATIONS
# --------------------------------------------------

@app.route("/recommend", methods=["POST"])
def recommend():

    try:
        movie_id = int(request.form.get("movie_id"))

        selected = movies_catalogue[
            movies_catalogue["movie_id"] == movie_id
        ]

        if selected.empty:
            raise ValueError("Selected movie was not found.")

        selected_movie = selected.iloc[0].to_dict()

        # Calculate content similarity
        similarity_results = calculate_all_similarities(
            movie_id,
            movies_catalogue,
            tfidf_matrix
        )

        # Merge content and popularity scores
        hybrid_df = merge_recommendation_scores(
            similarity_results,
            normalized_movies
        )

        # Handle missing ratings
        hybrid_df = handle_missing_ratings(hybrid_df)

        # Calculate hybrid scores
        hybrid_df = calculate_hybrid_score(hybrid_df)

        # Get top 10 recommendations
        result = recommend_hybrid_movies(
            hybrid_df,
            top_n=10
        )

        recommendations = result.to_dict(orient="records")

        return render_template(
            "recommendations.html",
            selected_movie=selected_movie,
            recommendations=recommendations
        )

    except (ValueError, TypeError) as exc:
        return render_template(
            "error.html",
            error=str(exc)
        ), 400


# --------------------------------------------------
# CATEGORY PAGE
# --------------------------------------------------

@app.route("/category/<int:cluster_id>")
def category(cluster_id):

    movies = get_movies_by_cluster(
        cluster_id,
        clustered_movies,
        top_n=20
    )

    if movies.empty:
        return "Category not found", 404

    category_name = movies.iloc[0]["cluster_name"]

    return render_template(
        "category.html",
        movies=movies.to_dict(orient="records"),
        category_name=category_name
    )


if __name__ == "__main__":
    app.run(debug=True)
