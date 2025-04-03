import pytest
from app import create_app
from database import db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base de datos en memoria para pruebas
    with app.app_context():
        db.create_all()  # Crear tablas antes de los tests
        yield app
        db.session.remove()
        db.drop_all()  # Limpiar base de datos después de los tests

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
