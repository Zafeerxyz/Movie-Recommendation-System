
import pandas as pd

def clean_list(value):

    if not isinstance(value, list):
        return []

    return [
        item.strip()
        for item in value
        if isinstance(item, str) and item.strip()
    ]


def validate_movie_data(df):
   

    checks = {
        "movie_id": df["movie_id"] <= 0,
        "runtime": df["runtime"] < 0,
        "vote_average": (
            (df["vote_average"] < 0)
            | (df["vote_average"] > 10)
        ),
        "vote_count": df["vote_count"] < 0,
        "popularity": df["popularity"] < 0
    }

    for column, condition in checks.items():
        invalid_count = condition.sum()

        if invalid_count > 0:
            raise ValueError(
                f"{column} contains {invalid_count} invalid values"
            )

    return True


def clean_movie_data(df):

    movies = df.copy()

    # Keep only the original TMDB columns
    original_columns = [
    "movie_id", "title", "overview", "genres", "release_date",
    "runtime", "vote_average", "vote_count", "popularity",
    "poster_path", "cast", "director", "keywords"
]

    movies = movies[original_columns]

    # Remove duplicate movie IDs
    movies = movies.drop_duplicates(subset="movie_id")

    # Convert numeric columns
    

    
    movies["runtime"] = pd.to_numeric(
        movies["runtime"], errors="coerce"
    ).astype("Int64")

    movies["vote_average"] = pd.to_numeric(
        movies["vote_average"], errors="coerce"
    ).astype("Float64")

    movies["vote_count"] = pd.to_numeric(
        movies["vote_count"], errors="coerce"
    ).astype("Int64")

    movies["popularity"] = pd.to_numeric(
        movies["popularity"], errors="coerce"
    ).astype("float64")

    # Treat unavailable zero values as missing
    zero_as_missing = [
        "runtime",
        "vote_average",
        "vote_count"
    ]

    for column in zero_as_missing:
        movies[column] = movies[column].replace(0, pd.NA)


    # Convert release dates
    movies["release_date"] = pd.to_datetime(
        movies["release_date"],
        errors="coerce"
    )

    
    
    # Clean list-based columns
    list_columns = [
        "genres",
        "cast",
        "director",
        "keywords"
    ]

    for column in list_columns:
        movies[column] = movies[column].apply(clean_list)

    # Clean text columns
    text_columns = ["title", "overview"]

    for column in text_columns:
        movies[column] = (
            movies[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    
    validate_movie_data(movies)
    
    return movies



