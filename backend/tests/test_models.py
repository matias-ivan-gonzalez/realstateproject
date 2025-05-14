import pytest
from app import create_app
from database import db
from models import User
from datetime import date
from models.Rol import Rol
from models.Permiso import Permiso
from models.User import Cliente, Administrador, Encargado, SuperUsuario
from models.Propiedad import Propiedad
from models.Imagen import Imagen

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        db.drop_all()
        db.create_all()
        from init_db import init_db
        init_db()
       
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
        db.session.rollback()

def test_create_cliente(db_session):
    cliente = User.Cliente(
        nombre='Juan',
        apellido='Pérez',
        dni='12345678',
        email='juanperez@example.com',
        contrasena='securepassword',
        telefono='1234567890',
        nacionalidad='Argentina',
        fecha_nacimiento=date(1990, 1, 1),  # Usa date() en lugar de cadena
        direccion='Calle Ficticia 123'
    )
    
    db_session.add(cliente)
    db_session.commit()
    
    retrieved_cliente = User.Cliente.query.filter_by(dni='12345678').first()
    
    assert retrieved_cliente is not None
    assert retrieved_cliente.email == 'juanperez@example.com'
    assert retrieved_cliente.nombre == 'Juan'
    assert retrieved_cliente.apellido == 'Pérez'


def test_cliente_repr(db_session):
    # Crear un cliente de ejemplo
    cliente = User.Cliente(
        nombre='Ana',
        apellido='Gómez',
        dni='87654321',
        email='anagomez@example.com',
        contrasena='anothersecurepassword',
        telefono='0987654321',
        nacionalidad='México',
        fecha_nacimiento=date(1985, 5, 15),  # Usa date() aquí también
        direccion='Av. Reforma 456'
    )
    
    db_session.add(cliente)
    db_session.commit()
    
    # Verificar el `repr()` del cliente después de que se haya guardado en la base de datos
    assert repr(cliente) == '<Cliente Ana Gómez>'
    


def test_db():
    admin = Administrador.query.filter_by(email='admin@uno.com').first()
    encargado = Encargado.query.filter_by(email='encargado@uno.com').first()
    cliente = Cliente.query.filter_by(email='cliente@uno.com').first()
    prop1 = Propiedad.query.filter_by(nombre='Casa Centro').first()
    prop2 = Propiedad.query.filter_by(nombre='Depto Norte').first()
    img1 = Imagen.query.filter_by(nombre_archivo='img1.jpg').first()

    assert Rol.query.count() >= 3, 'No se cargaron roles'
    assert Permiso.query.count() >= 2, 'No se cargaron permisos'
    assert SuperUsuario.query.count() >= 1, 'No se cargó superusuario'
    assert Administrador.query.count() >= 1, 'No se cargó administrador'
    assert Encargado.query.count() >= 1, 'No se cargó encargado'
    assert Cliente.query.count() >= 1, 'No se cargó cliente'
    assert Propiedad.query.count() >= 2, 'No se cargaron propiedades'
    assert admin in prop1.administradores, 'No se asignó administrador a propiedad'
    assert prop1 in admin.propiedades_administradas, 'No se asignó propiedad a administrador'
    assert prop1 in cliente.favoritos, 'No se asignó favorito'
    assert prop1.encargado == encargado, 'No se asignó encargado a propiedad'
    assert img1 in prop1.imagenes, 'No se asignó imagen a propiedad'
    print('Tests automáticos OK 1')

def test_models():
    admin = Administrador.query.filter_by(email='admin@uno.com').first()
    encargado = Encargado.query.filter_by(email='encargado@uno.com').first()
    cliente = Cliente.query.filter_by(email='cliente@uno.com').first()
    superuser = SuperUsuario.query.filter_by(email='super@user.com').first()
    prop1 = Propiedad.query.filter_by(nombre='Casa Centro').first()
    prop2 = Propiedad.query.filter_by(nombre='Depto Norte').first()
    img1 = Imagen.query.filter_by(nombre_archivo='img1.jpg').first()
    img2 = Imagen.query.filter_by(nombre_archivo='img2.jpg').first()

    # Roles
    assert Rol.query.filter_by(nombre='superusuario').first(), 'No existe rol superusuario'
    assert Rol.query.filter_by(nombre='admin').first(), 'No existe rol admin'
    assert Rol.query.filter_by(nombre='cliente').first(), 'No existe rol cliente'
    assert Rol.query.filter_by(nombre='encargado').first(), 'No existe rol encargado'

    # Permisos
    for nombre in [
        'crear_propiedad', 'eliminar_propiedad', 'modificar_propiedad', 'ver_propiedades',
        'crear_encargado', 'eliminar_encargado', 'asignar_propiedad_encargado', 'desasignar_propiedad_encargado',
        'crear_admin', 'eliminar_admin', 'ver_encargados', 'ver_administradores', 'añadir_favorito', 'eliminar_favorito']:
        assert Permiso.query.filter_by(nombre=nombre).first(), f'No existe permiso {nombre}'

    # Usuarios
    assert superuser, 'No se cargó superusuario'
    assert admin, 'No se cargó administrador'
    assert encargado, 'No se cargó encargado'
    assert cliente, 'No se cargó cliente'

    # Propiedades
    assert prop1, 'No se cargó propiedad Casa Centro'
    assert prop2, 'No se cargó propiedad Depto Norte'

    # Relación muchos-a-muchos administradores-propiedades
    assert admin in prop1.administradores, 'No se asignó admin a Casa Centro'
    assert admin in prop2.administradores, 'No se asignó admin a Depto Norte'
    assert prop1 in admin.propiedades_administradas, 'No se asignó Casa Centro a admin'
    assert prop2 in admin.propiedades_administradas, 'No se asignó Depto Norte a admin'

    # Favoritos
    assert prop1 in cliente.favoritos, 'No se asignó Casa Centro como favorito al cliente'

    # Encargado
    assert prop1.encargado == encargado, 'No se asignó encargado a Casa Centro'
    assert prop2.encargado == encargado, 'No se asignó encargado a Depto Norte'

    # Superusuario
    assert prop1.superusuario == superuser, 'No se asignó superusuario a Casa Centro'
    assert prop2.superusuario == superuser, 'No se asignó superusuario a Depto Norte'

    # Imagenes
    assert img1 in prop1.imagenes, 'No se asignó img1 a Casa Centro'
    assert img2 in prop2.imagenes, 'No se asignó img2 a Depto Norte'

    # Permisos asignados a roles
    rol_superusuario = Rol.query.filter_by(nombre='superusuario').first()
    rol_admin = Rol.query.filter_by(nombre='admin').first()
    rol_cliente = Rol.query.filter_by(nombre='cliente').first()
    rol_encargado = Rol.query.filter_by(nombre='encargado').first()
    crear_propiedad = Permiso.query.filter_by(nombre='crear_propiedad').first()
    ver_propiedades = Permiso.query.filter_by(nombre='ver_propiedades').first()
    añadir_favorito = Permiso.query.filter_by(nombre='añadir_favorito').first()
    assert crear_propiedad in rol_superusuario.permisos, 'Permiso crear_propiedad no asignado a superusuario'
    assert crear_propiedad in rol_admin.permisos, 'Permiso crear_propiedad no asignado a admin'
    assert ver_propiedades in rol_encargado.permisos, 'Permiso ver_propiedades no asignado a encargado'
    assert añadir_favorito in rol_cliente.permisos, 'Permiso añadir_favorito no asignado a cliente'

    print('Todos los tests automáticos de modelos pasaron OK') 


