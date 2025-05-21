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

def test_update_user(repo, app, sample_user):
    with app.app_context():
        # Crear un usuario inicial
        user = repo.create_usuario(sample_user)
        user_id = user.id
        
        # Datos de actualización
        update_data = {
            'nombre': 'Pedro',
            'apellido': 'Gomez',
            'email': 'pedro@mail.com',
            'telefono': '987654'
        }
        
        # Actualizar usuario
        updated_user = repo.update_user(user_id, update_data)
        
        # Verificar que los campos se actualizaron correctamente
        assert updated_user.nombre == 'Pedro'
        assert updated_user.apellido == 'Gomez'
        assert updated_user.email == 'pedro@mail.com'
        assert updated_user.telefono == '987654'
        
        # Verificar que los campos no actualizados mantienen su valor original
        assert updated_user.dni == sample_user['dni']
        assert updated_user.direccion == sample_user['direccion']
        
        # Verificar que se lanza error cuando el usuario no existe
        with pytest.raises(ValueError, match="Usuario no encontrado"):
            repo.update_user(99999, update_data)

def test_get_by_id(repo, app, sample_user):
    with app.app_context():
        # Verificar que no existe un usuario con ID 1
        assert repo.get_by_id(1) is None
        
        # Crear un usuario
        user = repo.create_usuario(sample_user)
        user_id = user.id
        
        # Verificar que podemos obtener el usuario por su ID
        retrieved_user = repo.get_by_id(user_id)
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.nombre == sample_user['nombre']
        assert retrieved_user.email == sample_user['email']
        assert retrieved_user.dni == sample_user['dni']

def test_create_superusuario_y_default(repo, app, sample_user):
    with app.app_context():
        # Test SuperUsuario
        super_user_data = sample_user.copy()
        super_user_data['email'] = 'super@mail.com'
        super_user_data['dni'] = '9999super'
        super_user_data['tipo'] = 'superusuario'
        # Eliminar campos específicos de cliente
        super_user_data.pop('fecha_nacimiento', None)
        super_user_data.pop('tarjeta', None)
        super_user_data.pop('direccion', None)
        
        super_user = repo.create_usuario(super_user_data)
        assert super_user.id is not None
        assert super_user.email == 'super@mail.com'
        assert super_user.dni == '9999super'
        assert super_user.tipo == 'superusuario'
        
        # Test caso por defecto (tipo no especificado)
        default_user_data = sample_user.copy()
        default_user_data['email'] = 'default@mail.com'
        default_user_data['dni'] = '9999default'
        # No especificamos tipo, debería usar el default 'cliente'
        
        default_user = repo.create_usuario(default_user_data)
        assert default_user.id is not None
        assert default_user.email == 'default@mail.com'
        assert default_user.dni == '9999default'
        assert default_user.tipo == 'cliente'  # Debería ser cliente por defecto

        # Test caso else (tipo no reconocido)
        unknown_user_data = sample_user.copy()
        unknown_user_data['email'] = 'unknown@mail.com'
        unknown_user_data['dni'] = '9999unknown'
        unknown_user_data['tipo'] = 'tipodesconocido'
        # Eliminar campos específicos de cliente
        unknown_user_data.pop('fecha_nacimiento', None)
        unknown_user_data.pop('tarjeta', None)
        unknown_user_data.pop('direccion', None)
        
        unknown_user = repo.create_usuario(unknown_user_data)
        assert unknown_user.id is not None
        assert unknown_user.email == 'unknown@mail.com'
        assert unknown_user.dni == '9999unknown'
        assert unknown_user.tipo == 'tipodesconocido'  # Debería mantener el tipo especificado
