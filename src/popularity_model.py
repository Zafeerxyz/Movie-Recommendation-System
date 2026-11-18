
def calculate_weighted_rating(df):
    """
    Calculate weighted ratings for all movies.

    R = Movie's average rating
    v = Number of votes
    C = Overall average rating
    m = Minimum vote threshold
    """

    movies = df.copy()

    C = movies["vote_average"].mean()
    m = movies["vote_count"].quantile(0.90)

    movies["weighted_rating"] = (
        (movies["vote_count"] / (movies["vote_count"] + m))
        * movies["vote_average"]
        +
        (m / (movies["vote_count"] + m))
        * C
    )

    movies = movies.dropna(
        subset=["vote_average", "vote_count", "weighted_rating"]
    )

    return movies


def get_popular_movies(df, top_n=10):
    """
    Return the top N movies ranked by weighted rating.
    """

    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")

    movies = calculate_weighted_rating(df)

    popular_movies = movies.sort_values(
        by="weighted_rating",
        ascending=False
    )

    return popular_movies[
        [
            "movie_id",
            "title",
            "genres",
            "vote_average",
            "vote_count",
            "weighted_rating"
        ]
    ].head(top_n).reset_index(drop=True)



def normalize_weighted_ratings(df):
    """
    Normalize weighted ratings to a 0-1 scale.
    """
    movies = df.copy()

    min_rating = movies["weighted_rating"].min()
    max_rating = movies["weighted_rating"].max()

    movies["normalized_rating"] = (
        (movies["weighted_rating"] - min_rating)
        / (max_rating - min_rating)
    )

    return movies