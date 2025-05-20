from unittest.mock import patch, MagicMock
import pytest
from models.user import Cliente, Administrador, Encargado, SuperUsuario
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
            contrasena='testpass123',
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
    print(response_post.data.decode('utf-8'))
    assert 'Mi Perfil'.encode("utf-8") in response_post.data
    assert 'Cerrar sesión'.encode("utf-8") in response_post.data

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
    with client.session_transaction() as sess:
        sess['rol'] = 'superusuario'
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
    html = response.data.decode('utf-8')
    print(html)
    assert 'Registro' in html and 'exitoso' in html

def test_agregar_empleado_dni_duplicado(client, app):
    with client.session_transaction() as sess:
        sess['rol'] = 'superusuario'
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
    html = response.data.decode('utf-8')
    print(html)
    assert 'dni' in html and 'registrado' in html

def test_agregar_empleado_email_duplicado(client, app):
    with client.session_transaction() as sess:
        sess['rol'] = 'superusuario'
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
    html = response.data.decode('utf-8')
    print(html)
    assert 'mail' in html and 'registrado' in html

def test_agregar_empleado_contrasena_corta(client, app):
    with client.session_transaction() as sess:
        sess['rol'] = 'superusuario'
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
    html = response.data.decode('utf-8')
    print(html)
    assert 'contraseña' in html and 'minimo' in html

def test_agregar_empleado_get(client):
    with client.session_transaction() as sess:
        sess['rol'] = 'superusuario'
    response = client.get('/empleados/nuevo')
    assert response.status_code == 200
    assert b'Agregar nuevo empleado' in response.data

def test_agregar_encargado_exitoso(client, app):
    with client.session_transaction() as sess:
        sess['rol'] = 'encargado'
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
    html = response.data.decode('utf-8')
    print(html)
    assert 'Registro' in html and 'exitoso' in html

def test_agregar_empleado_rol_invalido(client, app):
    with client.session_transaction() as sess:
        sess['rol'] = 'encargado'
    data = {
        'nombre': 'Invalido',
        'apellido': 'Error',
        'dni': '77777777',
        'telefono': '11-0000-0000',
        'nacionalidad': 'Desconocida',
        'email': 'error@gmail.com',
        'contrasena': '123456',
        'rol': 'Administrador'  # No permitido para 'encargado'
    }
    response = client.post('/empleados/nuevo', data=data, follow_redirects=True)
    html = response.data.decode('utf-8')
    print(html)
    assert 'permiso' in html and 'rol' in html

def test_logout(client, app):
    # Simula un usuario logueado
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = 'Test'
    response = client.post('/logout', follow_redirects=True)
    assert response.status_code == 200
    # Verifica que la sesión se haya limpiado
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'user_name' not in sess
    # Verifica que el mensaje de logout esté presente
    assert b'Sesi' in response.data and b'cerrada' in response.data

def test_login_superusuario(client, app):
    superuser = SuperUsuario(nombre='Super', apellido='User', email='super@user.com', contrasena='123', telefono='123', nacionalidad='AR', dni='100')
    superuser.id = 99
    with patch('architectural_patterns.service.user_service.UserService.authenticate_user', return_value=superuser):
        response = client.post('/login', data={'email': 'super@user.com', 'password': '123'}, follow_redirects=True)
        with client.session_transaction() as sess:
            assert sess['rol'] == 'superusuario'
            assert sess['user_name'] == 'Super'

def test_login_administrador(client, app):
    admin = Administrador(nombre='Admin', apellido='Uno', email='admin@uno.com', contrasena='123', telefono='123', nacionalidad='AR', dni='101')
    admin.id = 101
    with patch('architectural_patterns.service.user_service.UserService.authenticate_user', return_value=admin):
        response = client.post('/login', data={'email': 'admin@uno.com', 'password': '123'}, follow_redirects=True)
        with client.session_transaction() as sess:
            assert sess['rol'] == 'administrador'
            assert sess['user_name'] == 'Admin'

def test_login_encargado(client, app):
    encargado = Encargado(nombre='Enc', apellido='Uno', email='enc@uno.com', contrasena='123', telefono='123', nacionalidad='AR', dni='102')
    encargado.id = 102
    with patch('architectural_patterns.service.user_service.UserService.authenticate_user', return_value=encargado):
        response = client.post('/login', data={'email': 'enc@uno.com', 'password': '123'}, follow_redirects=True)
        with client.session_transaction() as sess:
            assert sess['rol'] == 'encargado'
            assert sess['user_name'] == 'Enc'

def test_login_cliente(client, app):
    cliente = Cliente(nombre='Cli', apellido='Uno', email='cli@uno.com', contrasena='123', telefono='123', nacionalidad='AR', dni='103')
    cliente.id = 103
    with patch('architectural_patterns.service.user_service.UserService.authenticate_user', return_value=cliente):
        response = client.post('/login', data={'email': 'cli@uno.com', 'password': '123'}, follow_redirects=True)
        with client.session_transaction() as sess:
            assert sess['rol'] == 'cliente'
            assert sess['user_name'] == 'Cli'

# pragma: no cover
