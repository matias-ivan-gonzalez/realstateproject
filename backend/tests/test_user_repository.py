import pytest
from architectural_patterns.repository.user_repository import UserRepository
from models.user import Cliente
from database import db
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def repo(app):
    return UserRepository()

@pytest.fixture
def sample_user():
    return {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'juan@mail.com',
        'contrasena': 'hash',
        'telefono': '123456',
        'fecha_nacimiento': None,
        'direccion': 'Calle Falsa 123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '1111'
    }

def test_create_and_get_by_email_and_dni(repo, app, sample_user):
    with app.app_context():
        # No existe aún
        assert repo.get_by_email(sample_user['email']) is None
        assert repo.get_by_dni(sample_user['dni']) is None
        # Crear usuario
        user = repo.create_usuario(sample_user)
        assert user.id is not None
        # Buscar por email
        user_by_email = repo.get_by_email(sample_user['email'])
        assert user_by_email is not None
        assert user_by_email.email == sample_user['email']
        # Buscar por dni
        user_by_dni = repo.get_by_dni(sample_user['dni'])
        assert user_by_dni is not None
        assert user_by_dni.dni == sample_user['dni']

def test_create_usuario_todos_los_tipos(repo, app, sample_user):
    tipos = ['cliente', 'administrador', 'encargado', 'superusuario']
    for tipo in tipos:
        user_data = sample_user.copy()
        user_data['email'] = f'{tipo}@mail.com'
        user_data['dni'] = f'9999{tipo}'
        user_data['tipo'] = tipo

        # Elimina campos que no corresponden según el tipo
        if tipo != 'cliente':
            user_data.pop('fecha_nacimiento', None)
            user_data.pop('tarjeta', None)
            user_data.pop('direccion', None)

        with app.app_context():
            user = repo.create_usuario(user_data)
            assert user.id is not None
            assert user.email == f'{tipo}@mail.com'
            assert user.dni == f'9999{tipo}'
            assert user.tipo == tipo
