import pytest
from app import create_app

# Fixture para inicializar la aplicación de prueba
@pytest.fixture
def client():
    app = create_app()
    app.testing = True  # Configurar el modo de prueba
    return app.test_client()

# Test para la ruta principal
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data  # Asegúrate de que se renderiza HTML

# Test para una ruta inexistente
def test_404(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404
