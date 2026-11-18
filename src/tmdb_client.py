
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"

ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise ValueError("TMDB_ACCESS_TOKEN is missing from .env")

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "accept": "application/json"
}




def get_tmdb_data(endpoint, params=None):

    url = f"{BASE_URL}/{endpoint}"
    max_retries = 4

    for attempt in range(max_retries):

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=30
            )

            # Handle rate limiting
            if response.status_code == 429:
                wait_time = 10
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            # Handle temporary server errors
            if response.status_code in [500, 502, 503, 504]:
                wait_time = 2 ** (attempt + 1)
                print(f"Server error: {response.status_code}")

                if attempt == max_retries - 1:
                    response.raise_for_status()

                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()

            return response.json()

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ) as error:

            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** (attempt + 1)

            print(f"Connection failed: {error}")
            print(f"Retrying in {wait_time} seconds...")

            time.sleep(wait_time)

    raise requests.exceptions.RetryError(
        f"Maximum retries exceeded for {endpoint}"
    )