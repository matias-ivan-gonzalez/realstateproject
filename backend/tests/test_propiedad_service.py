import pytest
from architectural_patterns.service.propiedad_service import PropiedadService

class MockPropiedadRepository:
    def __init__(self):
        self.propiedades = []
    def crear_propiedad(self, data):
        # Simula unicidad por nombre
        if any(p['nombre'] == data['nombre'] for p in self.propiedades):
            raise Exception("Ya existe una propiedad con ese nombre.")
        self.propiedades.append(data)
        return data
    def get_by_nombre(self, nombre):
        return next((p for p in self.propiedades if p['nombre'] == nombre), None)

@pytest.fixture
def propiedad_service():
    repo = MockPropiedadRepository()
    return PropiedadService(repository=repo)

def base_data():
    return {
        "nombre": "Casa Test",
        "ubicacion": "Calle 123",
        "precio": "100000",
        "cantidad_habitaciones": "3",
        "limite_personas": "5",
        "pet_friendly": True,
        "cochera": False,
        "wifi": True,
        "piscina": False,
        "patio_trasero": True,
        "descripcion": "Propiedad de prueba"
    }

def test_crear_propiedad_campo_obligatorio(propiedad_service):
    for field in ["nombre", "ubicacion", "precio", "cantidad_habitaciones", "limite_personas"]:
        data = base_data()
        data[field] = ""
        success, msg = propiedad_service.crear_propiedad(data)
        assert not success
        assert field in msg

def test_crear_propiedad_valores_invalidos(propiedad_service):
    data = base_data()
    data["precio"] = "noesnumero"
    success, msg = propiedad_service.crear_propiedad(data)
    assert not success
    assert "numéric" in msg.lower()

def test_crear_propiedad_nombre_repetido(propiedad_service):
    data = base_data()
    propiedad_service.crear_propiedad(data)
    success, msg = propiedad_service.crear_propiedad(data)
    assert not success
    assert "existe" in msg.lower()

def test_crear_propiedad_exitoso(propiedad_service):
    data = base_data()
    success, msg = propiedad_service.crear_propiedad(data)
    assert success
    assert "guardada" in msg.lower()

def test_crear_propiedad_excepcion_en_repository_service():
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