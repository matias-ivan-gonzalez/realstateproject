import pytest
from app import create_app
from database import db
from models import User
from datetime import date
from models.rol import Rol
from models.permiso import Permiso
from models.user import Cliente, Administrador, Encargado, SuperUsuario
from models.propiedad import Propiedad
from models.imagen import Imagen

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
    

def test_imagen_repr(db_session):
    img = Imagen.query.first()
    assert isinstance(img.__repr__(), str)

def test_propiedad_repr(db_session):
    prop = Propiedad.query.first()
    assert isinstance(prop.__repr__(), str)





