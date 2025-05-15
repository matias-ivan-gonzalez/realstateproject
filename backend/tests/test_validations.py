import pytest
from backend.utils.validations import tiene_permiso

class MockPermiso:
    def __init__(self, nombre):
        self.nombre = nombre

class MockRol:
    def __init__(self, permisos):
        self.permisos = permisos

class MockUsuario:
    def __init__(self, rol):
        self.rol = rol

def test_tiene_permiso_true():
    permisos = [MockPermiso('ver_propiedades'), MockPermiso('editar_usuario')]
    rol = MockRol(permisos)
    usuario = MockUsuario(rol)
    assert tiene_permiso(usuario, 'ver_propiedades') is True
    assert tiene_permiso(usuario, 'editar_usuario') is True

def test_tiene_permiso_false():
    permisos = [MockPermiso('ver_propiedades')]
    rol = MockRol(permisos)
    usuario = MockUsuario(rol)
    assert tiene_permiso(usuario, 'eliminar_usuario') is False

def test_tiene_permiso_sin_permisos():
    rol = MockRol([])
    usuario = MockUsuario(rol)
    assert tiene_permiso(usuario, 'ver_propiedades') is False
