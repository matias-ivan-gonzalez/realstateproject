import pytest
from architectural_patterns.service.empleado_service import EmpleadoService
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.get_by_dni.return_value = None
    repo.get_by_email.return_value = None
    repo.create_empleado.return_value = None
    return repo

@pytest.fixture
def empleado_service(mock_repository):
    return EmpleadoService(repository=mock_repository)

@patch('architectural_patterns.service.empleado_service.session', {})
def test_campos_obligatorios(empleado_service):
    data = {"nombre": "", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "obligatorio" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
def test_contrasena_corta(empleado_service):
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "contraseña" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
def test_dni_duplicado(empleado_service, mock_repository):
    mock_repository.get_by_dni.return_value = object()
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "dni" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
def test_email_duplicado(empleado_service, mock_repository):
    mock_repository.get_by_email.return_value = object()
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "mail" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'encargado'})
def test_rol_no_permitido(empleado_service):
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "permiso" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
def test_rol_inexistente(empleado_service):
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "NoExiste"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "permiso" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
@patch('architectural_patterns.service.empleado_service.Rol')
def test_rol_db_no_encontrado(mock_Rol, empleado_service):
    mock_Rol.query.filter_by.return_value.first.return_value = None
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "existe" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
@patch('architectural_patterns.service.empleado_service.Rol')
def test_exito(mock_Rol, empleado_service, mock_repository):
    mock_Rol.query.filter_by.return_value.first.return_value = object()
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert ok and "exitoso" in msg

@patch('architectural_patterns.service.empleado_service.session', {'rol': 'superusuario'})
@patch('architectural_patterns.service.empleado_service.Rol')
def test_excepcion_en_repository(mock_Rol, empleado_service, mock_repository):
    mock_Rol.query.filter_by.return_value.first.return_value = object()
    mock_repository.create_empleado.side_effect = Exception("error grave")
    data = {"nombre": "A", "apellido": "A", "dni": "1", "telefono": "1", "nacionalidad": "A", "email": "a@a.com", "contrasena": "123456", "rol": "Administrador"}
    ok, msg = empleado_service.crear_empleado(data)
    assert not ok and "Error al registrar" in msg 