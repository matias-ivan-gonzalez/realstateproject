import pytest
from init_db import init_db
from database import db

def test_init_db_runs(app):
    with app.app_context():
        db.create_all()  # Asegura que las tablas existen
        try:
            init_db()
        except Exception as e:
            pytest.fail(f"init_db lanzó una excepción inesperada: {e}")