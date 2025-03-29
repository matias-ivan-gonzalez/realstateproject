import pytest
from app import create_app

# Fixture para crear la app y un cliente de prueba
@pytest.fixture
def client():
    app = create_app()  # Crear la app usando la función que tienes en 'app.py'
    app.testing = True  # Habilitar modo de prueba
    return app.test_client()  # Crear un cliente para enviar solicitudes HTTP
