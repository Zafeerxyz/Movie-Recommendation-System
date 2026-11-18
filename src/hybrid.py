def merge_recommendation_scores(similarity_results, normalized_movies):
    """
    Merge content similarity scores with normalized ratings.
    """
    hybrid_df = similarity_results.merge(
        normalized_movies[
            ["movie_id", "weighted_rating", "normalized_rating"]
        ],
        on="movie_id",
        how="left"
    )

    return hybrid_df


def handle_missing_ratings(df):
    """
    Identify movies with and without rating information.
    Preserve missing ratings.
    """
    hybrid_df = df.copy()

    hybrid_df["rating_available"] = (
        hybrid_df["weighted_rating"].notna()
    )

    hybrid_df.loc[
        ~hybrid_df["rating_available"],
        "normalized_rating"
    ] = float("nan")

    return hybrid_df



def calculate_hybrid_score(df):
    """
    Calculate hybrid scores using content similarity
    and normalized ratings.
    """
    hybrid_df = df.copy()

    hybrid_df["hybrid_score"] = hybrid_df["similarity_score"]

    mask = hybrid_df["rating_available"]

    hybrid_df.loc[mask, "hybrid_score"] = (
        0.8 * hybrid_df.loc[mask, "similarity_score"]
        + 0.2 * hybrid_df.loc[mask, "normalized_rating"]
    )

    return hybrid_df



def recommend_hybrid_movies(df, top_n=10):
    """
    Return top-N movies ranked by hybrid score.
    """
    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")

    recommendations = df.sort_values(
        by="hybrid_score",
        ascending=False
    )

    columns = [
    "movie_id", "title", "genres", "poster_path",
    "similarity_score", "weighted_rating",
    "normalized_rating", "rating_available",
    "hybrid_score"
    ]

    return recommendations[columns].head(top_n).reset_index(drop=True)