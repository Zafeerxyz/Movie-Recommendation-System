import json

from pathlib import Path
from src.data_collection import get_movie_posters

# Load existing movie records
data_path = Path("data/raw/movies_raw.json")

with open(data_path, "r", encoding="utf-8") as file:
    movies = json.load(file)

print("Existing movies:", len(movies))

# Collect poster paths from TMDB popular pages
poster_lookup = get_movie_posters(total_pages=250)

# Check how many existing movies match
matched = sum(
    str(movie["movie_id"]) in poster_lookup
    for movie in movies
)

print("\nPoster lookup results")
print("Unique movie IDs found:", len(poster_lookup))
print("Existing movies matched:", matched)
print("Movies not matched:", len(movies) - matched)