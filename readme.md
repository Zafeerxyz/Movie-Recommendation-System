# 🎬 CineMatch – Hybrid Movie Recommendation System

CineMatch is a movie recommendation system that helps users discover movies based on their interests. It combines content-based filtering and popularity-based ranking to generate personalized movie recommendations using movie metadata collected from the TMDB API.

The project uses Python, Machine Learning, Flask, and the TMDB API to build an end-to-end movie recommendation application.

## 🚀 Features

- **Movie Search:** Search movies by title.
- **Content-Based Recommendations:** Find similar movies using genres, overview, cast, directors, and keywords.
- **Popularity-Based Ranking:** Rank movies using weighted ratings.
- **Hybrid Recommendation:** Combine content similarity and movie ratings.
- **TMDB Integration:** Retrieve movie details, cast, keywords, and poster information.
- **Movie Posters:** Display posters in search results and recommendations.
- **Model Persistence:** Save and load trained recommendation artifacts.
- **Checkpoint-Based Data Collection:** Resume data collection without restarting from the beginning.

## 🧠 Recommendation Approach

CineMatch uses a hybrid recommendation approach combining two methods.

### 1. Content-Based Filtering

The system combines the following movie attributes:

- Overview
- Genres
- Cast
- Directors
- Keywords

These attributes are combined into a single text feature.

TF-IDF (Term Frequency–Inverse Document Frequency) converts the combined text into numerical vectors. Cosine similarity is then used to identify movies with similar content.

### 2. Popularity-Based Ranking

The system uses a weighted rating formula to account for both average ratings and vote counts.

This prevents movies with very few votes from automatically receiving the highest ranking.

Weighted ratings are normalized to a 0–1 scale.

### 3. Hybrid Recommendation

The final recommendation score combines content similarity and normalized weighted ratings.

**For movies with available ratings:**

- 70% Content Similarity
- 30% Normalized Weighted Rating

**For movies without available ratings:**

- Content Similarity alone

This allows the system to recommend movies even when rating information is unavailable.

## 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Text Vectorization | TF-IDF |
| Similarity Measurement | Cosine Similarity |
| API Integration | TMDB API, Requests |
| Web Framework | Flask |
| Model Persistence | Joblib, SciPy |
| Frontend | HTML, CSS |
| Environment Management | Python-dotenv |

## 📁 Project Structure

```text
MovieRecommendation/
│
├── src/
│   ├── content_model.py
│   ├── data_collection.py
│   ├── evaluation.py
│   ├── feature_engineering.py
│   ├── hybrid.py
│   ├── persistence.py
│   ├── popularity_model.py
│   ├── preprocessing.py
│   └── tmdb_client.py
│
├── data/
│   └── raw/
│          ├── discovery_progress.json
│          ├── failed_movie_ids.json
│          ├── failed_poster_ids.json
│          ├── missing_poster_checkpoint.json
│          ├── missing_poster_progress.json
│          ├── movie_ids.json
│          ├── movies_raw_before_posters.json
│          ├── movies_raw.json
│          ├── poster_checkpoint.json
│         ├── poster_progress.json
│   └── processed/
          └── movies_processed.csv
│
├── notebooks/
│   └── movie_recommendation.ipynb
│
├── outputs/
│   └── models/
│       ├── movies_catalogue.joblib
│       ├── tfidf_matrix.npz
│       └── tfidf_vectorizer.joblib
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── tests/
    └── api_test.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd MovieRecommendation
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure TMDB API credentials

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_bearer_token
```

Keep `.env` out of version control. Never commit your API credentials.

### 5. Run the application

```bash
python app.py
```

Open your browser at:

```text
http://127.0.0.1:5000/
```

**Note:** The application requires the saved model artifacts and movie catalogue under `outputs/models/`. The repository must include these artifacts or provide instructions for generating them before running the application.

## 📊 Model Artifacts

The recommendation system uses three saved artifacts:

| Artifact | Description |
|---|---|
| `tfidf_vectorizer.joblib` | Fitted TF-IDF vectorizer |
| `tfidf_matrix.npz` | Sparse TF-IDF feature matrix |
| `movies_catalogue.joblib` | Processed movie catalogue |

These artifacts are loaded when the Flask application starts, avoiding the need to rebuild the recommendation model for every request.

## 🔄 Project Workflow

1. Collect movie information through the TMDB API.
2. Preprocess and clean the collected movie data.
3. Perform feature engineering by combining movie metadata.
4. Generate TF-IDF vectors.
5. Calculate content similarity using cosine similarity.
6. Calculate popularity-based weighted ratings.
7. Combine both approaches using hybrid scoring.
8. Save the trained artifacts.
9. Serve recommendations through the Flask application.

## 🔮 Future Improvements

- Migrate the Flask application to FastAPI.
- Develop REST API endpoints for movie recommendations.
- Improve recommendation quality through user feedback.
- Experiment with different hybrid scoring weights.
- Add automated testing and recommendation evaluation.
- Improve API reliability with retries and better error handling.
- Explore collaborative filtering and more advanced recommendation techniques.

## 🙏 Acknowledgements

Movie information and poster metadata are collected using the [TMDB API](https://developer.themoviedb.org/).

This product uses the TMDB API but is not endorsed or certified by TMDB.

---

**CineMatch – Discover movies you'll love.**
