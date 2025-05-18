from unittest.mock import patch
import pytest
from models.user import Cliente
from werkzeug.security import generate_password_hash

# Test para la ruta '/'
def test_index(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/')
        assert response.status_code == 200

# Test para la ruta '/login'
def test_login(client, app):
    # GET debe renderizar el formulario
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Iniciar sesión'.encode("utf-8") in response.data

    # Crear un usuario válido en la base de datos
    with app.app_context():
        user = Cliente(
            nombre='Test',
            apellido='User',
            email='testuser@mail.com',
            contrasena=generate_password_hash('testpass123'),
            telefono='123456',
            nacionalidad='Argentina',
            dni='12345678'
        )
        from database import db
        db.session.add(user)
        db.session.commit()

    # Login exitoso
    response_post = client.post('/login', data={'email': 'testuser@mail.com', 'password': 'testpass123'}, follow_redirects=True)
    assert response_post.status_code == 200
    assert 'Mi Perfil'.encode("utf-8") in response_post.data
    with client.session_transaction() as sess:
        assert sess['user_id']
        assert sess['user_name'] == 'Test'

    # Login fallido
    response_post_fail = client.post('/login', data={'email': 'testuser@mail.com', 'password': 'wrongpass'}, follow_redirects=True)
    assert response_post_fail.status_code == 200
    assert b'Email o contrase' in response_post_fail.data

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
    response = client.post('/propiedades/nueva', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'guardada exitosamente' in response.data

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
    response = client.get('/propiedades/modificar')
    assert response.status_code == 200

def test_agregar_empleado_exitoso(client, app):
    data = {
        'nombre': 'Juan',
        'apellido': 'Castro',
        'dni': '23446446',
        'telefono': '11-2234-3435',
        'nacionalidad': 'Argentina',
        'email': 'juan@gmail.com',
        'contrasena': '123456',
        'rol': 'Administrador'
    }
    response = client.post('/empleados/nuevo', data=data, follow_redirects=True)
    assert b'Registro exitoso' in response.data

def test_agregar_empleado_dni_duplicado(client, app):
    data = {
        'nombre': 'Juan',
        'apellido': 'Castro',
        'dni': '22333111',
        'telefono': '11-2234-3435',
        'nacionalidad': 'Argentina',
        'email': 'leo@gmail.com',
        'contrasena': '123456',
        'rol': 'Administrador'
    }
    client.post('/empleados/nuevo', data=data, follow_redirects=True)
    data2 = data.copy()
    data2['email'] = 'otro@gmail.com'
    response = client.post('/empleados/nuevo', data=data2, follow_redirects=True)
    assert b'Registro fallido. El dni ingresado ya se encuentra registrado' in response.data

def test_agregar_empleado_email_duplicado(client, app):
    data = {
        'nombre': 'Diego',
        'apellido': 'Perez',
        'dni': '22333112',
        'telefono': '11-2234-3435',
        'nacionalidad': 'Argentina',
        'email': 'diego@gmail.com',
        'contrasena': '123456',
        'rol': 'Administrador'
    }
    client.post('/empleados/nuevo', data=data, follow_redirects=True)
    data2 = data.copy()
    data2['dni'] = '99999999'
    response = client.post('/empleados/nuevo', data=data2, follow_redirects=True)
    assert b'Registro fallido. El mail ingresado ya se encuentra registrado' in response.data

def test_agregar_empleado_contrasena_corta(client, app):
    data = {
        'nombre': 'Ana',
        'apellido': 'Lopez',
        'dni': '88888888',
        'telefono': '11-2234-3435',
        'nacionalidad': 'Argentina',
        'email': 'ana@gmail.com',
        'contrasena': '123',
        'rol': 'Administrador'
    }
    response = client.post('/empleados/nuevo', data=data, follow_redirects=True)
    assert b'Registro fallido. La contrase' in response.data

def test_agregar_empleado_get(client):
    response = client.get('/empleados/nuevo')
    assert response.status_code == 200
    assert b'Agregar nuevo empleado' in response.data

def test_agregar_encargado_exitoso(client, app):
    data = {
        'nombre': 'Pedro',
        'apellido': 'Gomez',
        'dni': '55555555',
        'telefono': '11-9999-9999',
        'nacionalidad': 'Argentina',
        'email': 'pedro.encargado@gmail.com',
        'contrasena': '123456',
        'rol': 'Encargado'
    }
    response = client.post('/empleados/nuevo', data=data, follow_redirects=True)
    assert b'Registro exitoso' in response.data

def test_agregar_empleado_rol_invalido(client, app):
    data = {
        'nombre': 'Invalido',
        'apellido': 'Error',
        'dni': '77777777',
        'telefono': '11-0000-0000',
        'nacionalidad': 'Desconocida',
        'email': 'error@gmail.com',
        'contrasena': '123456',
        'rol': 'OtroRolQueNoExiste'
    }
    with pytest.raises(ValueError):
        client.post('/empleados/nuevo', data=data, follow_redirects=True)

# pragma: no cover
