import requests
import time


import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env")

headers = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}


# url = "https://api.themoviedb.org/3/movie/popular"


movie_id = 687163

url = f"https://api.themoviedb.org/3/movie/{movie_id}"

params = {
    "language": "en-US"
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30
)

response.raise_for_status()

movie_details = response.json()

# print("Title:", movie_details["title"])
# print("Overview:", movie_details["overview"])
# print("Genres:", movie_details["genres"])
# print("Runtime:", movie_details["runtime"])
# print("Rating:", movie_details["vote_average"])


credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"

credits_response = requests.get(
    credits_url,
    headers=headers,
    timeout=30
)

credits_response.raise_for_status()

credits = credits_response.json()

cast = sorted(
    credits["cast"],
    key=lambda actor: actor["order"]
)

top_cast = [
    actor["name"]
    for actor in cast[:5]
]

directors = [
    member["name"]
    for member in credits["crew"]
    if member["job"] == "Director"
]

# print("Cast:", top_cast)
# print("Director:", directors)



keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords"

keywords_response = requests.get(
    keywords_url,
    headers=headers,
    timeout=30
)

keywords_response.raise_for_status()

keywords_data = keywords_response.json()

movie_keywords = [
    keyword["name"]
    for keyword in keywords_data["keywords"]
]

# print("Keywords:", movie_keywords)

movie_record = {
    "movie_id": movie_id,
    "title": movie_details["title"],
    "overview": movie_details["overview"],
    "genres": [
        genre["name"]
        for genre in movie_details["genres"]
    ],
    "release_date": movie_details["release_date"],
    "runtime": movie_details["runtime"],
    "vote_average": movie_details["vote_average"],
    "vote_count": movie_details["vote_count"],
    "popularity": movie_details["popularity"],
    "poster_path": movie_details.get("poster_path"),
    "cast": top_cast,
    "director": directors,
    "keywords": movie_keywords,
    
}

print(movie_record)

poster_path = movie_record["poster_path"]

if poster_path:
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    print("Poster URL:", poster_url)
else:
    print("Poster not available")