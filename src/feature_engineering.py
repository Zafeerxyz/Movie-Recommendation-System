def combine_movie_features(row):
    
    
    overview = row["overview"]
    genres = " ".join(row["genres"])
    keywords = " ".join(row["keywords"])
    cast = " ".join(row["cast"])
    director = " ".join(row["director"])

    combined_text = " ".join([
        overview, genres, keywords, cast, director
    ])

    return combined_text


def create_combined_features(df):
    movies = df.copy()

    movies["combined_features"] = movies.apply(
        combine_movie_features,
        axis=1
    )

    return movies