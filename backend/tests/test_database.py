import pytest
from database import db
from flask_sqlalchemy import SQLAlchemy
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def test_db_instance():
    assert isinstance(db, SQLAlchemy), "db no es una instancia de SQLAlchemy"
    assert hasattr(db, 'session'), "db no tiene una sesión configurada"
    assert hasattr(db, 'Model'), "db no tiene el atributo Model"

def test_db_engine(app):
    with app.app_context():
        assert db.engine is not None, "db.engine no debería ser None dentro del contexto de la aplicación"
