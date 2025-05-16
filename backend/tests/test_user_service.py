import pytest
from architectural_patterns.service.user_service import UserService

class MockUserRepository:
    def __init__(self):
        self.users = []
    def get_by_email(self, email):
        return next((u for u in self.users if u['email'] == email), None)
    def get_by_dni(self, dni):
        return next((u for u in self.users if u['dni'] == dni), None)
    def create_cliente(self, user_dict):
        self.users.append(user_dict)
        return user_dict

@pytest.fixture
def user_service():
    repo = MockUserRepository()
    return UserService(user_repository=repo)

def test_register_email_repetido(user_service):
    user_service.user_repository.create_cliente({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 'dni': '12345678', 'tarjeta': ''
    })
    data = {
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'jp@mail.com', 'password': '12345678',
        'telefono': '456', 'f_nac': '2000-01-01', 'domicilio': 'Otra', 'nacionalidad': 'Argentina', 'dni': '87654321', 'tarjeta': ''
    }
    success, msg = user_service.register_user(data)
    assert not success
    assert 'email' in msg.lower()

def test_register_dni_repetido(user_service):
    user_service.user_repository.create_cliente({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp2@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 'dni': '11111111', 'tarjeta': ''
    })
    data = {
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'nuevo@mail.com', 'password': '12345678',
        'telefono': '456', 'f_nac': '2000-01-01', 'domicilio': 'Otra', 'nacionalidad': 'Argentina', 'dni': '11111111', 'tarjeta': ''
    }
    success, msg = user_service.register_user(data)
    assert not success
    assert 'dni' in msg.lower()

def test_register_fecha_invalida(user_service):
    data = {
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'nuevo2@mail.com', 'password': '12345678',
        'telefono': '456', 'f_nac': '2023-99-99', 'domicilio': 'Otra', 'nacionalidad': 'Argentina', 'dni': '22222222', 'tarjeta': ''
    }
    success, msg = user_service.register_user(data)
    assert not success
    assert 'fecha' in msg.lower()

def test_register_exitoso(user_service):
    data = {
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'nuevo3@mail.com', 'password': '12345678',
        'telefono': '456', 'f_nac': '2000-01-01', 'domicilio': 'Otra', 'nacionalidad': 'Argentina', 'dni': '33333333', 'tarjeta': '1234'
    }
    success, msg = user_service.register_user(data)
    assert success
    assert 'exitoso' in msg.lower()
    # Verifica que el usuario fue guardado
    user = user_service.user_repository.get_by_email('nuevo3@mail.com')
    assert user is not None
    assert user['dni'] == '33333333'
