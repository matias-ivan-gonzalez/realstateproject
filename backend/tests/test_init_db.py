import pytest
from backend.init_db import init_db

def test_init_db_runs(app):
    # Solo verifica que la función se ejecuta sin lanzar excepciones
    try:
        init_db()
    except Exception as e:
        pytest.fail(f"init_db lanzó una excepción inesperada: {e}") 