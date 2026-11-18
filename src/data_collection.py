
from src.tmdb_client import get_tmdb_data
    
import pandas as pd
import time
import requests

import json
from pathlib import Path


def get_movie_record(movie_id):

    # 1. Movie details
    movie_details = get_tmdb_data(
        f"movie/{movie_id}",
        params={"language": "en-US"}
    )

    # 2. Movie credits
    credits = get_tmdb_data(
        f"movie/{movie_id}/credits"
    )

    # 3. Movie keywords
    keywords_data = get_tmdb_data(
        f"movie/{movie_id}/keywords"
    )

    # 4. Extract cast
    cast = sorted(
        credits["cast"],
        key=lambda actor: actor["order"]
    )

    top_cast = [
        actor["name"] for actor in cast[:5]
    ]

    # 5. Extract directors
    directors = [
        member["name"]
        for member in credits["crew"]
        if member["job"] == "Director"
    ]

    # 6. Extract keywords
    movie_keywords = [
        keyword["name"]
        for keyword in keywords_data["keywords"]
    ]

    # 7. Create movie record
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
        "cast": top_cast,
        "director": directors,
        "keywords": movie_keywords
    }

    return movie_record


# if __name__ == "__main__":

#     movie = get_movie_record(687163)

#     print(movie["title"])
#     print(movie["genres"])
#     print(movie["director"])


# def collect_movies(movie_ids):
#     movie_records = []
    
#     for movie_id in movie_ids:
        
#         try:
#             movie = get_movie_record(movie_id)
#             movie_records.append(movie)
            
#             print(f"collected:{movie['title']}")
#         except requests.exceptions.RequestException as error:
#             print(f"Failed to collect movie {movie_id}: {error}")

#         time.sleep(1)


#     return movie_records





# movies_df = pd.DataFrame(movie_records)

# print("\nDataset shape:", movies_df.shape)

# print("\nFirst five records:")
# print(movies_df.head())

# print("\nDataset information:")
# movies_df.info()



# # Define raw data file path
# output_path = Path("data/raw/movies_raw.json")

# # Save original movie records
# with open(output_path, "w", encoding="utf-8") as file:
#     json.dump(
#         movie_records,
#         file,
#         indent=4,
#         ensure_ascii=False
#     )

# print("Raw dataset saved successfully!")



def save_checkpoint(movie_records):
    output_path = Path("data/raw/movies_checkpoint.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            movie_records,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"Checkpoint saved: {len(movie_records)} movies")
    
# save_checkpoint(movie_records)


def load_checkpoint():
    
    checkpoint_path = Path("data/raw/movies_checkpoint.json")

    if checkpoint_path.exists():

        with open(checkpoint_path, "r", encoding="utf-8") as file:
            movie_records = json.load(file)

        print(f"Loaded checkpoint: {len(movie_records)} movies")

        return movie_records

    return []

# existing_movies = load_checkpoint()

# print(len(existing_movies)) 



# collected_ids = {
#     movie["movie_id"]
#     for movie in existing_movies
# }

# print("Collected movie IDs:", collected_ids)


def collect_movies(movie_ids):
    
    movie_records = load_checkpoint()

    collected_ids = {
        movie["movie_id"]
        for movie in movie_records
    }

    failed_ids = []

    for movie_id in movie_ids:

        if movie_id in collected_ids:
            print(f"Skipping movie ID: {movie_id}")
            continue

        try:
            movie = get_movie_record(movie_id)

            movie_records.append(movie)
            collected_ids.add(movie_id)

            save_checkpoint(movie_records)

            print(f"Collected: {movie['title']}")

        except requests.exceptions.RequestException as error:

            print(f"Failed movie ID {movie_id}: {error}")

            failed_ids.append(movie_id)
            save_failed_ids(failed_ids)

        time.sleep(1)

    save_failed_ids(failed_ids)

    return movie_records


# movie_ids = [687163, 1423191, 1263337, 155, 1368337]

# movie_records = collect_movies(movie_ids)

# print("Total movies:", len(movie_records))


def get_movie_ids(page=1):
    
    response = get_tmdb_data(
        "movie/popular",
        params={
            "language": "en-US",
            "page": page
        }
    )

    movie_ids = [
        movie["id"]
        for movie in response["results"]
    ]

    return movie_ids


 
    
    
    
def collect_movie_ids(total_pages):
    
    all_movie_ids = load_movie_ids()

    collected_ids = set(all_movie_ids)

    last_page = load_discovery_progress()

    print(f"Resuming from page: {last_page + 1}")

    for page in range(last_page + 1, total_pages + 1):

        try:
            movie_ids = get_movie_ids(page)

            new_ids = [
                movie_id
                for movie_id in movie_ids
                if movie_id not in collected_ids
            ]

            all_movie_ids.extend(new_ids)
            collected_ids.update(new_ids)

            save_movie_ids(all_movie_ids)

            # Save progress only after successful page processing
            save_discovery_progress(page)

            print(
                f"Page {page}: "
                f"{len(new_ids)} new IDs collected"
            )

        except requests.exceptions.RequestException as error:
            print(f"Failed at page {page}: {error}")
            break

        time.sleep(0.5)

    return all_movie_ids


def save_movie_ids(movie_ids):
    
    output_path = Path("data/raw/movie_ids.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            movie_ids,
            file,
            indent=4
        )

    print(f"Saved {len(movie_ids)} movie IDs")
    

    
    
def load_movie_ids():
    
    file_path = Path("data/raw/movie_ids.json")

    if file_path.exists():

        with open(file_path, "r", encoding="utf-8") as file:
            movie_ids = json.load(file)

        print(f"Loaded {len(movie_ids)} existing movie IDs")

        return movie_ids

    return []

# if __name__ == "__main__":
    
#     movie_ids = load_movie_ids()

#     print("Total IDs:", len(movie_ids))
    
# if __name__ == "__main__":
    
#     movie_ids = collect_movie_ids(total_pages=3)

#     print("\nTotal unique IDs:", len(movie_ids))
    
def save_discovery_progress(page):
    
    progress_path = Path("data/raw/discovery_progress.json")

    progress = {
        "last_completed_page": page
    }

    with open(progress_path, "w", encoding="utf-8") as file:
        json.dump(
            progress,
            file,
            indent=4
        )

    print(f"Discovery progress saved: page {page}")
    
def load_discovery_progress():
    
    progress_path = Path("data/raw/discovery_progress.json")

    if progress_path.exists():

        with open(progress_path, "r", encoding="utf-8") as file:
            progress = json.load(file)

        return progress["last_completed_page"]

    return 0

if __name__ == "__main__":
    
    movie_ids = collect_movie_ids(total_pages=250)

    print("\nTotal unique IDs:", len(movie_ids))
    
    
    
    
def save_failed_ids(failed_ids):
    
    output_path = Path("data/raw/failed_movie_ids.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(failed_ids, file, indent=4)

    print(f"Saved {len(failed_ids)} failed movie IDs")
    
if __name__ == "__main__":
    
    movie_ids = load_movie_ids()

    print("Total movie IDs:", len(movie_ids))

    movie_records = collect_movies(movie_ids)

    print("\nTotal movies collected:", len(movie_records))