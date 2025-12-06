def get_logger(name: str = "app"):
    """Retourner un logger (config plus tard)."""
    class _Dummy:
        def info(self, *a, **k): pass
        def warning(self, *a, **k): pass
        def error(self, *a, **k): pass
    return _Dummy()