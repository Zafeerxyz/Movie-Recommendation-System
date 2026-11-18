
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_tfidf_matrix(df):
   

    if "combined_features" not in df.columns:
        raise ValueError("combined_features column is missing")

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        df["combined_features"]
    )

    return vectorizer, tfidf_matrix


def recommend_movies(movie_id, df, tfidf_matrix, top_n=10):
    """
    Recommend movies based on content similarity.

    Returns:
        DataFrame containing recommended movies and similarity scores
    """

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")

    if len(df) != tfidf_matrix.shape[0]:
        raise ValueError(
            "DataFrame and TF-IDF matrix must have the same number of rows"
        )

    # Find the selected movie's row position
    movie_positions = np.flatnonzero(
        df["movie_id"].to_numpy() == movie_id
    )
    
    if len(movie_positions) == 0:
        raise ValueError(f"Movie ID {movie_id} not found")

    movie_position = movie_positions[0]

    # Calculate similarity with every movie
    similarity_scores = cosine_similarity(
        tfidf_matrix[movie_position],
        tfidf_matrix
    ).flatten()

    # Sort movies by similarity, highest first
    similar_positions = np.argsort(
        similarity_scores
    )[::-1]

    # Exclude the selected movie
    similar_positions = [
        position
        for position in similar_positions
        if position != movie_position
    ]

    # Select Top-N recommendations
    top_positions = similar_positions[:top_n]

    recommendations = df.iloc[top_positions][
        [
            "movie_id",
            "title",
            "genres",
            "vote_average",
            "vote_count",
            "popularity"
        ]
    ].copy()

    recommendations["similarity_score"] = (
        similarity_scores[top_positions]
    )

    return recommendations.reset_index(drop=True)
