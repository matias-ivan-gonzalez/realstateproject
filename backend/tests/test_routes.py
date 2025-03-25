import pytest
from app import create_app

# Fixture para crear la app y un cliente de prueba
@pytest.fixture
def client():
    app = create_app()  # Crear la app usando la función que tienes en 'app.py'
    app.testing = True  # Habilitar modo de prueba
    return app.test_client()  # Crear un cliente para enviar solicitudes HTTP

# Test para la ruta '/'
def test_index(client):
    # Realiza una solicitud GET a la ruta '/'
    response = client.get('/')
    
    # Verifica que la respuesta tenga el código de estado 200
    assert response.status_code == 200
    
    # Verifica que el texto principal esté presente
    assert b'Frontend levantado desde Flask' in response.data
    
    # Verifica que los archivos estáticos estén incluidos (por ejemplo, Bootstrap CSS)
    assert b'href="/static/css/bootstrap.min.css"' in response.data
    assert b'src="/static/js/bootstrap.bundle.min.js"' in response.data
