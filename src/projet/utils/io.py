"""Utilitaires pour la lecture/écriture de fichiers."""
import json
import pandas as pd
from pathlib import Path
from typing import Any, Union


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Charge des données depuis un fichier CSV."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {path}")
    
    if path.suffix == '.csv':
        return pd.read_csv(path)
    else:
        raise ValueError(f"Format non supporté: {path.suffix}")


def save_data(data: Union[pd.DataFrame, dict], file_path: Union[str, Path]) -> None:
    """Sauvegarde des données vers un fichier."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(data, pd.DataFrame):
        if path.suffix == '.csv':
            data.to_csv(path, index=False)
        else:
            raise ValueError(f"Format non supporté pour DataFrame: {path.suffix}")
    elif isinstance(data, dict):
        if path.suffix == '.json':
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Format non supporté pour dict: {path.suffix}")
    else:
        raise ValueError(f"Type de données non supporté: {type(data)}")


def ensure_dir(path):
    """Créer un dossier si besoin (implémentation plus tard)."""
    return None