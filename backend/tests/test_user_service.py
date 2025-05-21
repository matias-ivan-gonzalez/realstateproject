import pytest
from architectural_patterns.service.user_service import UserService

class MockUser:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class MockUserRepository:
    def __init__(self):
        self.users = []
        self._next_id = 1
    def get_by_email(self, email):
        return next((u for u in self.users if u.email == email), None)
    def get_by_dni(self, dni):
        return next((u for u in self.users if u.dni == dni), None)
    def get_by_id(self, user_id):
        return next((u for u in self.users if u.id == user_id), None)
    def create_usuario(self, user_dict):
        user = MockUser(**user_dict)
        user.id = self._next_id
        self._next_id += 1
        self.users.append(user)
        return user
    def update_user(self, user_id, user_dict):
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Actualizar los campos del usuario
        for key, value in user_dict.items():
            setattr(user, key, value)
        
        return user

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
    user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 'dni': '12345678', 'tarjeta': ''
    })
    data = base_data()
    data['email'] = 'jp@mail.com'
    success, msg = user_service.register_user(data)
    assert not success
    assert 'email' in msg.lower()

def test_register_dni_repetido(user_service):
    user_service.user_repository.create_usuario({
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
    assert user.dni == data['dni']

def test_parse_fecha_nacimiento_none(user_service):
    assert user_service.parse_fecha_nacimiento(None) is None
    assert user_service.parse_fecha_nacimiento('') is None

@pytest.mark.parametrize('tipo', ['cliente', 'administrador', 'encargado', 'superusuario'])
def test_login_todos_los_tipos(user_service, tipo):
    data = base_data()
    data['tipo'] = tipo
    data['email'] = f'{tipo}@mail.com'
    data['dni'] = f'1000{tipo}'
    user_service.user_repository.create_usuario({
        'nombre': data['nombre'],
        'apellido': data['apellido'],
        'email': data['email'],
        'contrasena': data['password'],
        'telefono': data['telefono'],
        'nacionalidad': data['nacionalidad'],
        'dni': data['dni'],
        'tipo': tipo
    })
    user = user_service.authenticate_user(data['email'], data['password'])
    assert user is not None
    assert user.tipo == tipo

def test_update_user_no_existe(user_service):
    data = base_data()
    success, msg = user_service.update_user(999, data)
    assert not success
    assert 'no encontrado' in msg.lower()

def test_update_user_campos_obligatorios(user_service):
    # Primero creamos un usuario
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    
    # Probamos cada campo obligatorio
    for field in ['nombre', 'apellido', 'email', 'telefono', 'nacionalidad', 'dni', 'f_nac', 'domicilio']:
        data = base_data()
        data[field] = ''
        success, msg = user_service.update_user(user.id, data)
        assert not success
        assert field in msg.lower()

def test_update_user_validaciones(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    
    # Test email inválido
    data = base_data()
    data['email'] = 'noesmail'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'email' in msg.lower()
    
    # Test DNI no numérico
    data = base_data()
    data['dni'] = 'abc123'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'dni' in msg.lower()
    
    # Test teléfono no numérico
    data = base_data()
    data['telefono'] = 'abc123'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'teléfono' in msg.lower()
    
    # Test nacionalidad inválida
    data = base_data()
    data['nacionalidad'] = 'NoExiste'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'nacionalidad' in msg.lower()
    
    # Test fecha de nacimiento inválida
    data = base_data()
    data['f_nac'] = '2023-99-99'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'fecha' in msg.lower()

def test_update_user_email_duplicado(user_service):
    # Crear dos usuarios
    user1 = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    user2 = user_service.user_repository.create_usuario({
        'nombre': 'Maria', 'apellido': 'Gomez', 'email': 'mg@mail.com', 'contrasena': 'hash',
        'telefono': '456', 'fecha_nacimiento': None, 'direccion': 'Otra', 'nacionalidad': 'Argentina', 
        'dni': '87654321', 'tarjeta': '', 'tipo': 'cliente'
    })
    
    # Intentar actualizar email de user1 al email de user2
    data = base_data()
    data['email'] = 'mg@mail.com'
    success, msg = user_service.update_user(user1.id, data)
    assert not success
    assert 'email' in msg.lower()

def test_update_user_dni_duplicado(user_service):
    # Crear dos usuarios
    user1 = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    user2 = user_service.user_repository.create_usuario({
        'nombre': 'Maria', 'apellido': 'Gomez', 'email': 'mg@mail.com', 'contrasena': 'hash',
        'telefono': '456', 'fecha_nacimiento': None, 'direccion': 'Otra', 'nacionalidad': 'Argentina', 
        'dni': '87654321', 'tarjeta': '', 'tipo': 'cliente'
    })
    
    # Intentar actualizar DNI de user1 al DNI de user2
    data = base_data()
    data['dni'] = '87654321'
    success, msg = user_service.update_user(user1.id, data)
    assert not success
    assert 'dni' in msg.lower()

def test_update_user_password(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    
    # Test password corta
    data = base_data()
    data['password'] = '123'
    data['password_confirm'] = '123'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'contraseña' in msg.lower()
    
    # Test passwords no coinciden
    data = base_data()
    data['password'] = '12345678'
    data['password_confirm'] = '87654321'
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'coinciden' in msg.lower()

def test_update_user_exitoso(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': None, 'direccion': 'Calle', 'nacionalidad': 'Argentina', 
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    
    # Datos de actualización
    data = base_data()
    data['password'] = 'nuevapass123'
    data['password_confirm'] = 'nuevapass123'
    
    success, msg = user_service.update_user(user.id, data)
    assert success
    assert 'actualizado exitosamente' in msg.lower()
    
    # Verificar que los datos se actualizaron correctamente
    updated_user = user_service.user_repository.get_by_id(user.id)
    assert updated_user.nombre == data['nombre']
    assert updated_user.apellido == data['apellido']
    assert updated_user.email == data['email']
    assert updated_user.telefono == data['telefono']
    assert updated_user.nacionalidad == data['nacionalidad']
    assert updated_user.dni == data['dni']
    assert updated_user.direccion == data['domicilio']
    assert updated_user.contrasena == data['password']
