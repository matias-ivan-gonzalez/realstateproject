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

def base_data():
    return {
        'nombre': 'Ana', 'apellido': 'Lopez', 'email': 'nuevo@mail.com', 'password': '12345678',
        'telefono': '456', 'f_nac': '2000-01-01', 'domicilio': 'Otra', 'nacionalidad': 'Argentina', 'dni': '87654321', 'tarjeta': '1234'
    }

def test_register_campo_obligatorio(user_service):
    for field in ['nombre', 'apellido', 'email', 'password', 'telefono', 'f_nac', 'domicilio', 'nacionalidad', 'dni']:
        data = base_data()
        data[field] = ''
        success, msg = user_service.register_user(data)
        assert not success
        assert field in msg

def test_register_email_invalido(user_service):
    data = base_data()
    data['email'] = 'noesmail'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'email' in msg.lower()

def test_register_password_corta(user_service):
    data = base_data()
    data['password'] = '123'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'contraseña' in msg.lower()

def test_register_dni_no_numerico(user_service):
    data = base_data()
    data['dni'] = 'abc123'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'dni' in msg.lower()

def test_register_telefono_no_numerico(user_service):
    data = base_data()
    data['telefono'] = 'abc123'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'teléfono' in msg.lower()

def test_register_tarjeta_no_numerica(user_service):
    data = base_data()
    data['tarjeta'] = 'abcd'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'tarjeta' in msg.lower()

def test_register_nacionalidad_invalida(user_service):
    data = base_data()
    data['nacionalidad'] = 'NoExiste'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'nacionalidad' in msg.lower()

def test_register_email_repetido(user_service):
    user_service.user_repository.create_cliente({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 'dni': '12345678', 'tarjeta': ''
    })
    data = base_data()
    data['email'] = 'jp@mail.com'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'email' in msg.lower()

def test_register_dni_repetido(user_service):
    user_service.user_repository.create_cliente({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp2@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 'dni': '11111111', 'tarjeta': ''
    })
    data = base_data()
    data['dni'] = '11111111'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'dni' in msg.lower()

def test_register_fecha_invalida(user_service):
    data = base_data()
    data['f_nac'] = '2023-99-99'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'fecha' in msg.lower()

def test_register_exitoso(user_service):
    data = base_data()
    success, msg = user_service.register_user(data)
    assert success
    assert 'exitoso' in msg.lower()
    # Verifica que el usuario fue guardado
    user = user_service.user_repository.get_by_email(data['email'])
    assert user is not None
    assert user['dni'] == data['dni']

def test_parse_fecha_nacimiento_none(user_service):
    assert user_service.parse_fecha_nacimiento(None) is None
    assert user_service.parse_fecha_nacimiento('') is None
