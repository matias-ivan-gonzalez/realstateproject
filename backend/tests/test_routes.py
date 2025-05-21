from unittest.mock import patch
import pytest
from models.user import Cliente, Administrador
from werkzeug.security import generate_password_hash
from database import db
from datetime import date

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

def test_perfil_get_renderiza_profile(client, app):
    # Crear usuario cliente
    with app.app_context():
        cliente = Cliente(
            nombre='Ana', apellido='Lopez', email='ana_perfil1@mail.com', contrasena='12345678',
            telefono='123', nacionalidad='Argentina', dni='12345679', fecha_nacimiento=date(2000, 1, 1),
            direccion='Calle', tarjeta='1111'
        )
        db.session.add(cliente)
        db.session.commit()
        cliente_id = cliente.id
    with client.session_transaction() as sess:
        sess['user_id'] = cliente_id
    response = client.get('/perfil')
    print('GET /perfil response:', response.data.decode('utf-8'))
    assert response.status_code == 200
    # Verifica que se muestra el formulario de perfil
    assert b'profile' in response.data or b'Perfil' in response.data or b'perfil' in response.data

def test_perfil_post_actualiza_y_error(client, app):
    # Crear usuario cliente
    with app.app_context():
        cliente = Cliente(
            nombre='Ana', apellido='Lopez', email='ana_perfil2@mail.com', contrasena='12345678',
            telefono='123', nacionalidad='Argentina', dni='12345680', fecha_nacimiento=date(2000, 1, 1),
            direccion='Calle', tarjeta='1111'
        )
        db.session.add(cliente)
        db.session.commit()
        cliente_id = cliente.id
    with client.session_transaction() as sess:
        sess['user_id'] = cliente_id
    # POST exitoso
    data = {
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'ana_perfil2@mail.com', 'telefono': '999',
        'nacionalidad': 'Argentina', 'dni': '12345680', 'password': '', 'password_confirm': '',
        'f_nac': '2000-01-01', 'domicilio': 'Calle', 'tarjeta': '1111'
    }
    print('POST /perfil data:', data)
    response_post = client.post('/perfil', data=data, follow_redirects=True)
    print('POST /perfil response:', response_post.data.decode('utf-8'))
    assert response_post.status_code == 200
    assert b'Perfil actualizado' in response_post.data or b'success' in response_post.data
    # POST error (campo obligatorio vacío)
    data['nombre'] = ''
    print('POST /perfil error data:', data)
    response_post_fail = client.post('/perfil', data=data, follow_redirects=True)
    print('POST /perfil error response:', response_post_fail.data.decode('utf-8'))
    assert b'obligatorio' in response_post_fail.data or b'danger' in response_post_fail.data

def test_login_required_redirige_si_no_logueado(client):
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get('/perfil', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_perfil_get_y_post_admin(client, app):
    # Crear usuario administrador
    with app.app_context():
        admin = Administrador(
            nombre='Admin', apellido='Sys', email='admin_perfil@mail.com', contrasena='12345678',
            telefono='123', nacionalidad='Argentina', dni='12345681'
        )
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
    with client.session_transaction() as sess:
        sess['user_id'] = admin_id
    # GET: debe mostrar el perfil sin campos de cliente
    response = client.get('/perfil')
    assert response.status_code == 200
    assert b'Admin' in response.data
    # POST exitoso (cambia el teléfono)
    data = {
        'nombre': 'Admin', 'apellido': 'Sys', 'email': 'admin_perfil@mail.com', 'telefono': '999',
        'nacionalidad': 'Argentina', 'dni': '12345681', 'password': '', 'password_confirm': ''
    }
    response_post = client.post('/perfil', data=data, follow_redirects=True)
    assert response_post.status_code == 200
    assert b'Perfil actualizado' in response_post.data or b'success' in response_post.data

# pragma: no cover
