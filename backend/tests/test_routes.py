from unittest.mock import patch
import pytest

# Test para la ruta '/'
def test_index(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/')
        assert response.status_code == 200

# Test para la ruta '/login'
def test_login(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/login')
        assert response.status_code == 200

        response_post = client.post('/login', data={})
        assert response_post.status_code == 200

# Test para la ruta '/register' (GET)
def test_register_get(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/register')
        assert response.status_code == 200

# Test para la ruta '/register' (POST)
def test_register_post(client):
    with patch('flask.render_template', return_value=''):
        response = client.post('/register', data={})
        assert response.status_code in (200, 302)

def test_register_post_success(client):
    # Datos válidos para registro exitoso
    data = {
        'nombre': 'Ana',
        'apellido': 'Lopez',
        'email': 'test_registro_exitoso@mail.com',
        'password': '12345678',
        'telefono': '456123',
        'f_nac': '2000-01-01',
        'domicilio': 'Otra',
        'nacionalidad': 'Argentina',
        'dni': '99999999',
        'tarjeta': '1234'
    }
    response = client.post('/register', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

# Test para la ruta '/propiedades/nueva' (GET)
def test_get_nueva_propiedad(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/propiedades/nueva')
        assert response.status_code == 200

# Test para la ruta '/propiedades/nueva' (POST) - éxito
def test_post_nueva_propiedad_success(client):
    data = {
        "nombre": "Casa Test",
        "ubicacion": "Calle 123",
        "precio": "100000",
        "cantidad_habitaciones": "3",
        "limite_personas": "5"
    }
    response = client.post('/propiedades/nueva', data=data, follow_redirects=False)
    # Puede redirigir o mostrar mensaje de éxito
    assert response.status_code in (200, 302)

# Test para la ruta '/propiedades/nueva' (POST) - faltan campos
def test_post_nueva_propiedad_faltan_campos(client):
    data = {
        "nombre": "",
        "ubicacion": "Calle 123",
        "precio": "100000",
        "cantidad_habitaciones": "3",
        "limite_personas": "5"
    }
    response = client.post('/propiedades/nueva', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'El campo nombre es obligatorio' in response.data

# Test para la ruta '/propiedades/nueva' (POST) - nombre repetido
def test_post_nueva_propiedad_nombre_repetido(client):
    data = {
        "nombre": "Casa Test",
        "ubicacion": "Calle 123",
        "precio": "100000",
        "cantidad_habitaciones": "3",
        "limite_personas": "5"
    }
    # Primer guardado
    client.post('/propiedades/nueva', data=data, follow_redirects=True)
    # Segundo guardado con el mismo nombre
    response = client.post('/propiedades/nueva', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Ya existe una propiedad con ese nombre' in response.data

def test_get_modificar_propiedad(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/propiedades/modificar')
        assert response.status_code == 200