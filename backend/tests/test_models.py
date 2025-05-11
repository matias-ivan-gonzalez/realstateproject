import pytest
from app import create_app
from database import db
from models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
    
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
    # Crear un cliente con los campos definidos en el modelo
    cliente = User.Cliente(
        nombre='Juan',
        apellido='Pérez',
        dni='12345678',
        email='juanperez@example.com',
        contrasena='securepassword',
        telefono='1234567890',
        nacionalidad='Argentina',
        fecha_nacimiento='1990-01-01',
        direccion='Calle Ficticia 123'
    )
    
    db_session.add(cliente)
    db_session.commit()
    
    # Recuperar el cliente de la base de datos para verificar su existencia
    retrieved_cliente = User.Cliente.query.filter_by(dni='12345678').first()
    
    # Asegurarse de que el cliente fue guardado y se recuperó correctamente
    assert retrieved_cliente is not None
    assert retrieved_cliente.email == 'juanperez@example.com'
    assert retrieved_cliente.nombre == 'Juan'
    assert retrieved_cliente.apellido == 'Pérez'


def test_cliente_repr():
    # Crear un cliente de ejemplo
    cliente = User.Cliente(
        nombre='Ana',
        apellido='Gómez',
        dni='87654321',
        email='anagomez@example.com',
        contrasena='anothersecurepassword',
        telefono='0987654321',
        nacionalidad='México',
        fecha_nacimiento='1985-05-15',
        direccion='Av. Reforma 456'
    )
    
    # Verificar el `repr()` del cliente
    assert repr(cliente) == '<Cliente Ana Gómez>'
