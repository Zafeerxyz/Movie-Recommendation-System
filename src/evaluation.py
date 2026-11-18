def calculate_genre_overlap(selected_genres, recommended_genres):
    """
    Calculate Jaccard similarity between two movies' genres.
    """
    selected_set = set(selected_genres)
    recommended_set = set(recommended_genres)

    intersection = selected_set.intersection(recommended_set)
    union = selected_set.union(recommended_set)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def evaluate_genre_overlap(selected_genres, recommendations):
    """
    Evaluate genre overlap for a list of recommended movies.
    """
    results = recommendations.copy()

    results["genre_overlap"] = results["genres"].apply(
        lambda genres: calculate_genre_overlap(
            selected_genres,
            genres
        )
    )

    return results



from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def calculate_diversity(recommendations, df, tfidf_matrix):
    
    """
    Calculate intra-list diversity using pairwise cosine similarity.
    """
    movie_ids = recommendations["movie_id"].tolist()

    positions = df.index[
        df["movie_id"].isin(movie_ids)
    ].tolist()

    recommendation_matrix = tfidf_matrix[positions]

    similarity_matrix = cosine_similarity(recommendation_matrix)

    upper_triangle = similarity_matrix[
        np.triu_indices(len(positions), k=1)
    ]

    diversity = 1 - upper_triangle.mean()

    return diversity