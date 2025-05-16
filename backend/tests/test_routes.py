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
        response = client.post('/register', data={}, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/login')

def test_get_nueva_propiedad(client):
    response = client.get('/propiedades/nueva')
    assert response.status_code == 200

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
