import json
import shutil
from pathlib import Path

raw_path = Path("data/raw/movies_raw.json")
popular_path = Path("data/raw/poster_checkpoint.json")
missing_path = Path("data/raw/missing_poster_checkpoint.json")

# 1. Create a backup
backup_path = Path("data/raw/movies_raw_before_posters.json")

if not backup_path.exists():
    shutil.copy2(raw_path, backup_path)

# 2. Load existing movie records
with open(raw_path, "r", encoding="utf-8") as file:
    movies = json.load(file)

# 3. Load both poster collections
with open(popular_path, "r", encoding="utf-8") as file:
    popular_posters = json.load(file)

with open(missing_path, "r", encoding="utf-8") as file:
    missing_posters = json.load(file)

# 4. Combine poster lookups
poster_lookup = {
    **popular_posters,
    **missing_posters
}

# 5. Update movie records
for movie in movies:
    movie_id = str(movie["movie_id"])

    if movie_id in poster_lookup:
        movie["poster_path"] = poster_lookup[movie_id]

# 6. Save updated records
with open(raw_path, "w", encoding="utf-8") as file:
    json.dump(movies, file, indent=4, ensure_ascii=False)

# 7. Verify results
available = sum(
    bool(movie.get("poster_path"))
    for movie in movies
)

print("Total movies:", len(movies))
print("Movies with posters:", available)
print("Movies without posters:", len(movies) - available)
print("Backup:", backup_path)