"""Pipeline: entraînement du modèle ML."""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path

from projet.utils.io import load_data, save_data


def run(
    dataset_path: str = "data/processed/dataset.csv",
    model_path: str = "models/artefacts/model.pkl",
    test_size: float = 0.2,
    random_state: int = 42
) -> None:
    """
    Pipeline d'entraînement du modèle.
    
    Args:
        dataset_path: Chemin vers le dataset traité
        model_path: Chemin de sauvegarde du modèle
        test_size: Proportion des données pour le test
        random_state: Seed pour la reproductibilité
    """
    print(f"🤖 Entraînement du modèle depuis {dataset_path}")
    
    # Charger le dataset
    df = load_data(dataset_path)
    print(f"📊 Dataset chargé: {df.shape}")
    
    # Préparer les features et target
    if 'target' in df.columns:
        X = df.drop(['target', 'species'], axis=1, errors='ignore')
        y = df['target']
    else:
        raise ValueError("Colonne 'target' manquante dans le dataset")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"✂️  Split: train={X_train.shape}, test={X_test.shape}")
    
    # Entraînement
    model = RandomForestClassifier(n_estimators=100, random_state=random_state)
    model.fit(X_train, y_train)
    print("🎯 Modèle entraîné")
    
    # Évaluation
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"📈 Accuracy: {accuracy:.3f}")
    
    # Rapport détaillé
    print("\n📋 Rapport de classification:")
    print(classification_report(y_test, y_pred))
    
    # Sauvegarder le modèle
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"💾 Modèle sauvegardé: {model_path}")
    
    # Sauvegarder les métriques
    metrics = {
        'accuracy': accuracy,
        'n_samples_train': len(X_train),
        'n_samples_test': len(X_test),
        'n_features': X.shape[1]
    }
    save_data(metrics, "reports/metrics/training_metrics.json")
    print("📊 Métriques sauvegardées")
    
    return model, metrics


if __name__ == "__main__":
    run()