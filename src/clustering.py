
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score
)

from src.persistence import load_artifacts


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

N_COMPONENTS = 100
N_CLUSTERS = 15
RANDOM_STATE = 42

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "outputs" / "models"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Human-readable labels assigned after inspecting
# the top genres and representative movies.
CLUSTER_LABELS = {
    0: "Superhero & Action",
    1: "Sci-Fi & Monsters",
    2: "Horror",
    3: "Martial Arts & Action",
    4: "Animation & Family",
    5: "Crime & Dark Comedy",
    6: "Psychological Horror",
    7: "Romance & Drama",
    8: "Mixed Collection",
    9: "Christmas & Family",
    10: "Comedy & Romance",
    11: "Space & Sci-Fi",
    12: "War & History",
    13: "Crime & Action Thriller",
    14: "Romance, Drama & Thriller"
}


# --------------------------------------------------
# 1. DIMENSIONALITY REDUCTION
# --------------------------------------------------

def reduce_dimensions(tfidf_matrix, n_components=N_COMPONENTS):

    svd = TruncatedSVD(
        n_components=n_components,
        random_state=RANDOM_STATE
    )

    reduced_matrix = svd.fit_transform(tfidf_matrix)

    explained_variance = svd.explained_variance_ratio_.sum()

    print("\nDIMENSIONALITY REDUCTION")
    print("-----------------------")
    print("Original shape:", tfidf_matrix.shape)
    print("Reduced shape:", reduced_matrix.shape)
    print("Explained variance:", round(explained_variance, 4))

    return svd, reduced_matrix


# --------------------------------------------------
# 2. EVALUATE DIFFERENT K VALUES
# --------------------------------------------------

def evaluate_kmeans(
    reduced_matrix,
    k_values=(5, 8, 10, 12, 15)
):

    results = []

    print("\nK-MEANS EVALUATION")
    print("------------------")

    for k in k_values:

        model = KMeans(
            n_clusters=k,
            random_state=RANDOM_STATE,
            n_init=10
        )

        labels = model.fit_predict(reduced_matrix)

        silhouette = silhouette_score(
            reduced_matrix,
            labels,
            sample_size=2000,
            random_state=RANDOM_STATE
        )

        db_score = davies_bouldin_score(
            reduced_matrix,
            labels
        )

        results.append({
            "k": k,
            "silhouette_score": silhouette,
            "davies_bouldin_score": db_score
        })

        print(
            f"K={k} | "
            f"Silhouette={silhouette:.4f} | "
            f"Davies-Bouldin={db_score:.4f}"
        )

    return pd.DataFrame(results)


# --------------------------------------------------
# 3. TRAIN FINAL K-MEANS MODEL
# --------------------------------------------------

def train_final_kmeans(
    reduced_matrix,
    movies_catalogue,
    k=N_CLUSTERS
):

    if reduced_matrix.shape[0] != len(movies_catalogue):
        raise ValueError(
            "TF-IDF rows and movie catalogue rows are not aligned."
        )

    kmeans = KMeans(
        n_clusters=k,
        random_state=RANDOM_STATE,
        n_init=10
    )

    cluster_labels = kmeans.fit_predict(reduced_matrix)

    clustered_movies = movies_catalogue.copy()

    clustered_movies["cluster"] = cluster_labels

    clustered_movies["cluster_name"] = (
        clustered_movies["cluster"].map(CLUSTER_LABELS)
    )

    return kmeans, clustered_movies


# --------------------------------------------------
# 4. CLUSTER SIZE SUMMARY
# --------------------------------------------------

def get_cluster_sizes(clustered_movies):

    cluster_sizes = (
        clustered_movies["cluster"]
        .value_counts()
        .sort_index()
        .rename_axis("cluster_id")
        .reset_index(name="movie_count")
    )

    cluster_sizes["cluster_name"] = (
        cluster_sizes["cluster_id"].map(CLUSTER_LABELS)
    )

    return cluster_sizes[
        ["cluster_id", "cluster_name", "movie_count"]
    ]


# --------------------------------------------------
# 5. CLUSTER PROFILING
# --------------------------------------------------

def profile_clusters(clustered_movies):

    print("\nCLUSTER PROFILES")
    print("----------------")

    for cluster_id in sorted(clustered_movies["cluster"].unique()):

        cluster_data = clustered_movies[
            clustered_movies["cluster"] == cluster_id
        ]

        top_genres = (
            cluster_data["genres"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
            .replace("", np.nan)
            .dropna()
            .value_counts()
            .head(5)
        )

        print(
            f"\nCluster {cluster_id}: "
            f"{CLUSTER_LABELS.get(cluster_id, 'Unlabelled')}"
        )

        print("Movies:", len(cluster_data))
        print("Top genres:")
        print(top_genres.to_dict())


# --------------------------------------------------
# 6. REPRESENTATIVE MOVIES
# --------------------------------------------------

def get_cluster_representatives(
    kmeans,
    reduced_matrix,
    clustered_movies,
    top_n=10
):

    representatives = {}

    for cluster_id in range(kmeans.n_clusters):

        positions = np.where(
            clustered_movies["cluster"].to_numpy() == cluster_id
        )[0]

        cluster_vectors = reduced_matrix[positions]

        centroid = kmeans.cluster_centers_[cluster_id]

        distances = np.linalg.norm(
            cluster_vectors - centroid,
            axis=1
        )

        closest_indices = np.argsort(distances)[:top_n]

        representative_positions = positions[closest_indices]

        representatives[cluster_id] = (
            clustered_movies.iloc[representative_positions][
                ["movie_id", "title", "genres"]
            ].copy()
        )

    return representatives


# --------------------------------------------------
# 7. CREATE REVIEWER SUMMARY
# --------------------------------------------------

def create_cluster_summary(
    clustered_movies,
    representatives
):

    summary = []

    for cluster_id in range(N_CLUSTERS):

        cluster_data = clustered_movies[
            clustered_movies["cluster"] == cluster_id
        ]

        top_genres = (
            cluster_data["genres"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
            .replace("", np.nan)
            .dropna()
            .value_counts()
            .head(5)
            .index
            .tolist()
        )

        representative_titles = (
            representatives[cluster_id]["title"]
            .head(5)
            .tolist()
        )

        summary.append({
            "cluster_id": cluster_id,
            "cluster_name": CLUSTER_LABELS.get(
                cluster_id, "Unlabelled"
            ),
            "movie_count": len(cluster_data),
            "top_genres": ", ".join(top_genres),
            "representative_movies": ", ".join(
                representative_titles
            )
        })

    return pd.DataFrame(summary)


# --------------------------------------------------
# 8. SAVE ARTIFACTS
# --------------------------------------------------

def save_clustering_artifacts(
    svd,
    kmeans,
    clustered_movies,
    evaluation_results,
    cluster_summary
):

    joblib.dump(
        svd,
        MODEL_DIR / "movie_svd.joblib"
    )

    joblib.dump(
        kmeans,
        MODEL_DIR / "movie_kmeans.joblib"
    )

    joblib.dump(
        clustered_movies,
        MODEL_DIR / "movies_clustered.joblib"
    )

    evaluation_results.to_csv(
        OUTPUT_DIR / "kmeans_evaluation.csv",
        index=False
    )

    cluster_summary.to_csv(
        OUTPUT_DIR / "cluster_summary.csv",
        index=False
    )

    print("\nARTIFACTS SAVED")
    print("---------------")
    print("SVD model:", MODEL_DIR / "movie_svd.joblib")
    print("K-Means model:", MODEL_DIR / "movie_kmeans.joblib")
    print("Clustered movies:", MODEL_DIR / "movies_clustered.joblib")
    print("Evaluation:", OUTPUT_DIR / "kmeans_evaluation.csv")
    print("Cluster summary:", OUTPUT_DIR / "cluster_summary.csv")


# --------------------------------------------------
# 9. MAIN EXECUTION
# --------------------------------------------------

def main():

    print("Loading movie recommendation artifacts...")

    _, tfidf_matrix, movies_catalogue = load_artifacts()

    print("Movie catalogue:", movies_catalogue.shape)
    print("TF-IDF matrix:", tfidf_matrix.shape)

    # Step 1: Reduce dimensions
    svd, reduced_matrix = reduce_dimensions(
        tfidf_matrix,
        n_components=N_COMPONENTS
    )

    # Step 2: Evaluate K values
    evaluation_results = evaluate_kmeans(
        reduced_matrix
    )

    # Step 3: Train final model
    kmeans, clustered_movies = train_final_kmeans(
        reduced_matrix,
        movies_catalogue,
        k=N_CLUSTERS
    )

    # Step 4: Cluster sizes
    cluster_sizes = get_cluster_sizes(clustered_movies)

    print("\nCLUSTER SIZES")
    print("-------------")
    print(cluster_sizes.to_string(index=False))

    # Step 5: Profile clusters
    profile_clusters(clustered_movies)

    # Step 6: Find representative movies
    representatives = get_cluster_representatives(
        kmeans,
        reduced_matrix,
        clustered_movies,
        top_n=10
    )

    print("\nREPRESENTATIVE MOVIES")
    print("--------------------")

    for cluster_id, movies in representatives.items():

        print(
            f"\nCluster {cluster_id}: "
            f"{CLUSTER_LABELS[cluster_id]}"
        )

        print(movies[["title", "genres"]].to_string(index=False))

    # Step 7: Create reviewer summary
    cluster_summary = create_cluster_summary(
        clustered_movies,
        representatives
    )

    # Step 8: Save everything
    save_clustering_artifacts(
        svd,
        kmeans,
        clustered_movies,
        evaluation_results,
        cluster_summary
    )




def get_movies_by_cluster(
    cluster_id,
    clustered_movies,
    top_n=20
):
    """
    Return movies belonging to a selected cluster.
    """

    cluster_data = clustered_movies[
        clustered_movies["cluster"] == cluster_id
    ].copy()

    if cluster_data.empty:
        return pd.DataFrame()

    cluster_data = cluster_data.sort_values(
        by=["vote_count", "popularity"],
        ascending=False
    )

    return cluster_data.head(top_n)

if __name__ == "__main__":
    
    import joblib

    clustered_movies = joblib.load(
        "outputs/models/movies_clustered.joblib"
    )

    movies = get_movies_by_cluster(
        cluster_id=11,
        clustered_movies=clustered_movies,
        top_n=10
    )

    print(
        movies[
            ["title", "genres", "vote_average", "poster_path"]
        ].to_string(index=False)
    )