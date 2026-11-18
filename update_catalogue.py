
import json
import joblib
import pandas as pd

from pathlib import Path
from src.preprocessing import clean_movie_data
from src.feature_engineering import create_combined_features

# Project paths
project_root = Path(__file__).resolve().parent
raw_path = project_root / "data" / "raw" / "movies_raw.json"
catalogue_path = (
    project_root / "outputs" / "models" / "movies_catalogue.joblib"
)

# 1. Load updated raw data
with open(raw_path, "r", encoding="utf-8") as file:
    movie_records = json.load(file)

movies_raw = pd.DataFrame(movie_records)

# 2. Apply existing preprocessing
movies_cleaned = clean_movie_data(movies_raw)

# 3. Recreate combined features
movies_featured = create_combined_features(movies_cleaned)

# 4. Verify poster column
print("Catalogue shape:", movies_featured.shape)
print("Poster column exists:", "poster_path" in movies_featured.columns)
print(
    "Movies with posters:",
    movies_featured["poster_path"].notna().sum()
)

# 5. Update only the catalogue artifact
joblib.dump(movies_featured, catalogue_path)

print("Movie catalogue updated successfully!")
