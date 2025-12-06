"""Pipeline: création du dataset depuis les données brutes."""
import pandas as pd
from pathlib import Path
from projet.utils.io import load_data, save_data


def run(input_path: str = "data/raw/iris.csv", output_path: str = "data/processed/dataset.csv") -> None:
    """
    Pipeline de création du dataset.
    
    Args:
        input_path: Chemin vers les données brutes
        output_path: Chemin de sortie du dataset traité
    """
    print(f"📊 Création du dataset depuis {input_path}")
    
    # Charger les données brutes
    try:
        df = load_data(input_path)
        print(f"✅ Données chargées: {df.shape}")
    except FileNotFoundError:
        # Créer un dataset d'exemple si pas de données
        print("⚠️  Fichier non trouvé, création d'un dataset d'exemple (Iris)")
        from sklearn.datasets import load_iris
        iris = load_iris()
        df = pd.DataFrame(iris.data, columns=iris.feature_names)
        df['target'] = iris.target
        df['species'] = [iris.target_names[i] for i in iris.target]
    
    # Nettoyage basique
    df = df.dropna()
    print(f"🧹 Données nettoyées: {df.shape}")
    
    # Sauvegarder
    save_data(df, output_path)
    print(f"💾 Dataset sauvegardé: {output_path}")
    
    return df


if __name__ == "__main__":
    run()