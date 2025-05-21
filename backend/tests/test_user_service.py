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

# Test para get_paises
def test_get_paises_coverage(user_service):
    paises = user_service.get_paises()
    assert isinstance(paises, list)
    assert len(paises) > 0

# Test para parse_fecha_nacimiento con valor inválido
def test_parse_fecha_nacimiento_invalid_coverage(user_service):
    fecha = user_service.parse_fecha_nacimiento('invalid-date')
    assert fecha is None

# Test para update_user con tarjeta no numérica
def test_update_user_tarjeta_no_numerica_coverage(user_service):
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': '2000-01-01', 'direccion': 'Calle', 'nacionalidad': 'Argentina',
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle',
        'tarjeta': 'abcd'
    }
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'tarjeta' in msg.lower()

# Test para update_user sin cambios
def test_update_user_sin_cambios_coverage(user_service):
    # Crear usuario inicial con los mismos campos que espera el servicio
    fecha_nacimiento = user_service.parse_fecha_nacimiento('2000-01-01')
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': fecha_nacimiento,  # Usamos el objeto date directamente
        'direccion': 'Calle',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'cliente'
    })

    # Forzar que el mock tenga todos los campos y tipos correctos
    user.fecha_nacimiento = fecha_nacimiento
    user.direccion = 'Calle'
    user.tipo = 'cliente'
    if not hasattr(user, 'tarjeta'):
        user.tarjeta = ''

    # Intentar actualizar con los mismos datos
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': fecha_nacimiento.strftime('%Y-%m-%d'),
        'domicilio': 'Calle',
        'tarjeta': ''
    }

    success, msg = user_service.update_user(user.id, data)

    assert not success
    assert 'cambio' in msg.lower()

# Test para update_user con email duplicado
def test_update_user_email_duplicado_coverage(user_service):
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': '2000-01-01', 'direccion': 'Calle', 'nacionalidad': 'Argentina',
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    user2 = user_service.user_repository.create_usuario({
        'nombre': 'Maria', 'apellido': 'Gomez', 'email': 'mg@mail.com', 'contrasena': 'hash',
        'telefono': '456', 'fecha_nacimiento': '2000-01-01', 'direccion': 'Otra', 'nacionalidad': 'Argentina',
        'dni': '87654321', 'tarjeta': '', 'tipo': 'cliente'
    })
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'mg@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle'
    }
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'email' in msg.lower()

# Test para update_user con dni duplicado
def test_update_user_dni_duplicado_coverage(user_service):
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan', 'apellido': 'Perez', 'email': 'jp@mail.com', 'contrasena': 'hash',
        'telefono': '123', 'fecha_nacimiento': '2000-01-01', 'direccion': 'Calle', 'nacionalidad': 'Argentina',
        'dni': '12345678', 'tarjeta': '', 'tipo': 'cliente'
    })
    user2 = user_service.user_repository.create_usuario({
        'nombre': 'Maria', 'apellido': 'Gomez', 'email': 'mg@mail.com', 'contrasena': 'hash',
        'telefono': '456', 'fecha_nacimiento': '2000-01-01', 'direccion': 'Otra', 'nacionalidad': 'Argentina',
        'dni': '87654321', 'tarjeta': '', 'tipo': 'cliente'
    })
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '87654321',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle'
    }
    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'dni' in msg.lower()

# Test para authenticate_user con usuario inexistente
def test_authenticate_user_no_existe_coverage(user_service):
    user = user_service.authenticate_user('noexiste@mail.com', 'password')
    assert user is None

# Test para parse_fecha_nacimiento con string vacío
def test_parse_fecha_nacimiento_empty_coverage(user_service):
    fecha = user_service.parse_fecha_nacimiento('')
    assert fecha is None

# Test para update_user con error en el repositorio
def test_update_user_repository_error_coverage(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': '2000-01-01',
        'direccion': 'Calle',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'cliente'
    })

    # Modificar el mock para que lance una excepción
    def mock_update_error(user_id, user_dict):
        raise Exception("Error simulado en el repositorio")
    
    user_service.user_repository.update_user = mock_update_error

    # Intentar actualizar
    data = {
        'nombre': 'Juan Modificado',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'error' in msg.lower()

# Test para update_user con contraseña
def test_update_user_with_password_coverage(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': '2000-01-01',
        'direccion': 'Calle',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'cliente'
    })

    # Intentar actualizar con nueva contraseña
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle',
        'password': 'nuevapass123',
        'password_confirm': 'nuevapass123'
    }

    success, msg = user_service.update_user(user.id, data)
    assert success
    assert 'exitosamente' in msg.lower()

# Test para update_user con contraseña corta
def test_update_user_short_password_coverage(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': '2000-01-01',
        'direccion': 'Calle',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'cliente'
    })

    # Intentar actualizar con contraseña corta
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle',
        'password': '123',
        'password_confirm': '123'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'contraseña' in msg.lower()

# Test para update_user con contraseñas que no coinciden
def test_update_user_password_mismatch_coverage(user_service):
    # Crear usuario inicial
    user = user_service.user_repository.create_usuario({
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': '2000-01-01',
        'direccion': 'Calle',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'cliente'
    })

    # Intentar actualizar con contraseñas diferentes
    data = {
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'jp@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle',
        'password': 'nuevapass123',
        'password_confirm': 'otrapass123'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'coinciden' in msg.lower()

# Test para update_user con administrador
def test_update_user_administrador_coverage(user_service):
    # Crear usuario administrador
    user = user_service.user_repository.create_usuario({
        'nombre': 'Admin',
        'apellido': 'Sistema',
        'email': 'admin@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': None,
        'direccion': 'Oficina',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'administrador'
    })

    # Intentar actualizar
    data = {
        'nombre': 'Admin',
        'apellido': 'Sistema',
        'email': 'admin@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'cambio' in msg.lower()

# Test para update_user con encargado
def test_update_user_encargado_coverage(user_service):
    # Crear usuario encargado
    user = user_service.user_repository.create_usuario({
        'nombre': 'Encargado',
        'apellido': 'Sistema',
        'email': 'encargado@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': None,
        'direccion': 'Oficina',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'encargado'
    })

    # Intentar actualizar
    data = {
        'nombre': 'Encargado',
        'apellido': 'Sistema',
        'email': 'encargado@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'cambio' in msg.lower()

# Test para update_user con superusuario
def test_update_user_superusuario_coverage(user_service):
    # Crear usuario superusuario
    user = user_service.user_repository.create_usuario({
        'nombre': 'Super',
        'apellido': 'Admin',
        'email': 'super@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': None,
        'direccion': 'Oficina',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'superusuario'
    })

    # Intentar actualizar
    data = {
        'nombre': 'Super',
        'apellido': 'Admin',
        'email': 'super@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'cambio' in msg.lower()

# Test para update_user con tipo inválido
def test_update_user_tipo_invalido_coverage(user_service):
    # Crear usuario con tipo inválido
    user = user_service.user_repository.create_usuario({
        'nombre': 'Usuario',
        'apellido': 'Invalido',
        'email': 'invalido@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': None,
        'direccion': 'Calle',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'tipo_invalido'
    })

    # Intentar actualizar
    data = {
        'nombre': 'Usuario',
        'apellido': 'Invalido',
        'email': 'invalido@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678'
    }

    success, msg = user_service.update_user(user.id, data)
    assert not success
    assert 'cambio' in msg.lower()

# Test para update_user con cliente y datos diferentes
def test_update_user_cliente_con_cambios_coverage(user_service):
    # Crear usuario cliente
    user = user_service.user_repository.create_usuario({
        'nombre': 'Cliente',
        'apellido': 'Test',
        'email': 'cliente@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': '2000-01-01',
        'direccion': 'Calle Original',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '',
        'tipo': 'cliente'
    })

    # Intentar actualizar con datos diferentes
    data = {
        'nombre': 'Cliente',
        'apellido': 'Test',
        'email': 'cliente@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-02',  # Cambiamos la fecha
        'domicilio': 'Calle Nueva',  # Cambiamos la dirección
        'tarjeta': '1234'  # Agregamos tarjeta
    }

    success, msg = user_service.update_user(user.id, data)
    assert success
    assert 'exitosamente' in msg.lower()

    # Verificar que los cambios se aplicaron
    updated_user = user_service.user_repository.get_by_id(user.id)
    assert updated_user.fecha_nacimiento == user_service.parse_fecha_nacimiento('2000-01-02')
    assert updated_user.direccion == 'Calle Nueva'
    assert updated_user.tarjeta == '1234'

def test_update_user_cliente_tarjeta_solo_coverage(user_service):
    # Crear usuario cliente
    fecha_nac = user_service.parse_fecha_nacimiento('2000-01-01')
    user = user_service.user_repository.create_usuario({
        'nombre': 'Cliente',
        'apellido': 'Test',
        'email': 'cliente@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': fecha_nac,
        'direccion': 'Calle Original',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'tarjeta': '1111',
        'tipo': 'cliente'
    })

    # Actualizar solo la tarjeta
    data = {
        'nombre': 'Cliente',
        'apellido': 'Test',
        'email': 'cliente@mail.com',
        'telefono': '123',
        'nacionalidad': 'Argentina',
        'dni': '12345678',
        'f_nac': '2000-01-01',
        'domicilio': 'Calle Original',
        'tarjeta': '2222'
    }

    success, msg = user_service.update_user(user.id, data)
    assert success
    assert 'exitosamente' in msg.lower()
    updated_user = user_service.user_repository.get_by_id(user.id)
    assert updated_user.tarjeta == '2222'

def test_update_user_no_cliente_coverage(user_service):
    # Crear usuario administrador
    user = user_service.user_repository.create_usuario({
        'nombre': 'Admin',
        'apellido': 'Test',
        'email': 'admin@mail.com',
        'contrasena': 'hash',
        'telefono': '123',
        'fecha_nacimiento': None,
        'direccion': 'Oficina',
        'nacionalidad': 'Argentina',
        'dni': '99999999',
        'tarjeta': '',
        'tipo': 'administrador'
    })

    # Actualizar un campo común
    data = {
        'nombre': 'Admin',
        'apellido': 'Test',
        'email': 'admin@mail.com',
        'telefono': '456',  # Cambiamos el teléfono
        'nacionalidad': 'Argentina',
        'dni': '99999999'
    }

    success, msg = user_service.update_user(user.id, data)
    assert success
    assert 'exitosamente' in msg.lower()
    updated_user = user_service.user_repository.get_by_id(user.id)
    assert updated_user.telefono == '456'
