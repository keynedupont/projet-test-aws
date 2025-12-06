def accuracy(y_true, y_pred):
    """Stub de métrique. Remplace-moi par de vraies métriques plus tard."""
    return float(sum(int(a == b) for a, b in zip(y_true, y_pred))) / max(1, len(y_true))