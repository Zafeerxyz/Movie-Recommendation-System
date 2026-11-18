import json
import time
import requests

from pathlib import Path
from src.tmdb_client import get_tmdb_data

# File paths
raw_path = Path("data/raw/movies_raw.json")
lookup_path = Path("data/raw/poster_checkpoint.json")
missing_path = Path("data/raw/missing_poster_checkpoint.json")
progress_path = Path("data/raw/missing_poster_progress.json")
failed_path = Path("data/raw/failed_poster_ids.json")

# Load original movies
with open(raw_path, "r", encoding="utf-8") as file:
    movies = json.load(file)

# Load existing poster lookup
with open(lookup_path, "r", encoding="utf-8") as file:
    poster_lookup = json.load(file)

# Identify unmatched movie IDs
missing_ids = [
    movie["movie_id"]
    for movie in movies
    if str(movie["movie_id"]) not in poster_lookup
]

print("Movies needing posters:", len(missing_ids))

# Load previous checkpoint
if missing_path.exists():
    with open(missing_path, "r", encoding="utf-8") as file:
        missing_posters = json.load(file)
else:
    missing_posters = {}

# Load progress
if progress_path.exists():
    with open(progress_path, "r", encoding="utf-8") as file:
        progress = json.load(file)
        last_index = progress["last_completed_index"]
else:
    last_index = 0

failed_ids = []

print(f"Resuming from index: {last_index + 1}")

for index in range(last_index, len(missing_ids)):

    movie_id = missing_ids[index]

    try:
        details = get_tmdb_data(
            f"movie/{movie_id}",
            params={"language": "en-US"}
        )

        missing_posters[str(movie_id)] = details.get("poster_path")

        # Save poster checkpoint
        with open(missing_path, "w", encoding="utf-8") as file:
            json.dump(missing_posters, file, indent=4)

        # Save progress
        with open(progress_path, "w", encoding="utf-8") as file:
            json.dump(
                {"last_completed_index": index + 1},
                file,
                indent=4
            )

        print(f"{index + 1}/{len(missing_ids)} completed: {movie_id}")

    except requests.exceptions.RequestException as error:
        print(f"Failed movie {movie_id}: {error}")
        failed_ids.append(movie_id)

        with open(failed_path, "w", encoding="utf-8") as file:
            json.dump(failed_ids, file, indent=4)

    time.sleep(0.5)

print("Missing poster collection completed.")