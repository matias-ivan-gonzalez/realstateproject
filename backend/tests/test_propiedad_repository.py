import pytest
from architectural_patterns.repository.propiedad_repository import PropiedadRepository
from architectural_patterns.service.propiedad_service import PropiedadService
from models.propiedad import Propiedad
from database import db
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def repo(app):
    return PropiedadRepository()

@pytest.fixture
def sample_propiedad():
    return {
        "nombre": "Casa Test",
        "ubicacion": "Calle 123",
        "precio": 100000.0,
        "cantidad_habitaciones": 3,
        "limite_personas": 5,
        "pet_friendly": True,
        "cochera": False,
        "wifi": True,
        "piscina": False,
        "patio_trasero": True,
        "descripcion": "Propiedad de prueba"
    }

def test_create_propiedad(repo, app, sample_propiedad):
    with app.app_context():
        propiedad = repo.crear_propiedad(sample_propiedad)
        assert propiedad.id is not None
        assert propiedad.nombre == sample_propiedad["nombre"]
        # Buscar por nombre
        propiedad_db = Propiedad.query.filter_by(nombre=sample_propiedad["nombre"]).first()
        assert propiedad_db is not None
        assert propiedad_db.ubicacion == sample_propiedad["ubicacion"]

def test_crear_propiedad_excepcion_en_repository():
    class FailingRepository:
        def get_by_nombre(self, nombre):
            return None
        def crear_propiedad(self, data):
            raise Exception("DB error")
    service = PropiedadService(repository=FailingRepository())
    data = {
        "nombre": "Casa Test",
        "ubicacion": "Calle 123",
        "precio": "100000",
        "cantidad_habitaciones": "3",
        "limite_personas": "5"
    }
    success, msg = service.crear_propiedad(data)
    assert not success
    assert "Error al guardar la propiedad" in msg