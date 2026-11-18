
from flask import Flask, render_template, request
import pandas as pd

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


app = Flask(__name__)

# Load saved artifacts once when the application starts
vectorizer, tfidf_matrix, movies_catalogue = load_artifacts()

# Prepare normalized ratings once
weighted_movies = calculate_weighted_rating(movies_catalogue)
normalized_movies = normalize_weighted_ratings(weighted_movies)


@app.route("/", methods=["GET", "POST"])
def home():

    search_results = []
    recommendations = []
    selected_movie = None
    error = None

    if request.method == "GET":
        query = request.args.get("q", "").strip()

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

    if request.method == "POST":
        try:
            movie_id = int(request.form.get("movie_id"))

            selected = movies_catalogue[
                movies_catalogue["movie_id"] == movie_id
            ]

            if selected.empty:
                raise ValueError("Selected movie was not found.")

            selected_movie = selected.iloc[0].to_dict()

            # Calculate similarity against the full catalogue
            similarity_results = calculate_all_similarities(
                movie_id,
                movies_catalogue,
                tfidf_matrix
            )

            # Build hybrid scores
            hybrid_df = merge_recommendation_scores(
                similarity_results,
                normalized_movies
            )

            hybrid_df = handle_missing_ratings(hybrid_df)
            hybrid_df = calculate_hybrid_score(hybrid_df)

            # Get top 10 recommendations
            result = recommend_hybrid_movies(
                hybrid_df,
                top_n=10
            )

            recommendations = result.to_dict(orient="records")

        except (ValueError, TypeError) as exc:
            error = str(exc)

    return render_template(
        "index.html",
        search_results=search_results,
        recommendations=recommendations,
        selected_movie=selected_movie,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
