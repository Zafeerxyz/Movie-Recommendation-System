import joblib
from pathlib import Path
from scipy.sparse import save_npz, load_npz


def save_artifacts(vectorizer, tfidf_matrix, movies_df):
    
    project_root = Path(__file__).resolve().parent.parent
    
    model_dir = project_root / "outputs" / "models"
    
    model_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(vectorizer, model_dir / "tfidf_vectorizer.joblib")
    
    save_npz(model_dir / "tfidf_matrix.npz", tfidf_matrix)
    
    joblib.dump(movies_df, model_dir / "movies_catalogue.joblib")

    print("Artifacts saved successfully.")


def load_artifacts():
    project_root = Path(__file__).resolve().parent.parent
    
    model_dir = project_root / "outputs" / "models"
    

    vectorizer = joblib.load(
        model_dir / "tfidf_vectorizer.joblib"
    )
    
    tfidf_matrix = load_npz(
        model_dir / "tfidf_matrix.npz"
    )
    
    movies_df = joblib.load(
        model_dir / "movies_catalogue.joblib"
    )

    return vectorizer, tfidf_matrix, movies_df