import pytest
from architectural_patterns.repository.empleado_repository import EmpleadoRepository
from unittest.mock import patch, MagicMock

@pytest.fixture
def repo():
    return EmpleadoRepository()

@patch('architectural_patterns.repository.empleado_repository.Administrador')
def test_get_administradores(mock_Admin, repo):
    mock_Admin.query.all.return_value = [object()]
    result = repo.get_administradores()
    assert isinstance(result, list)

@patch('architectural_patterns.repository.empleado_repository.Encargado')
def test_get_encargados(mock_Encargado, repo):
    mock_Encargado.query.all.return_value = [object()]
    result = repo.get_encargados()
    assert isinstance(result, list)

@patch('architectural_patterns.repository.empleado_repository.Administrador')
@patch('architectural_patterns.repository.empleado_repository.Encargado')
def test_get_empleado_by_id(mock_Encargado, mock_Admin, repo):
    mock_Admin.query.get.return_value = None
    mock_Encargado.query.get.return_value = 'encargado'
    result = repo.get_empleado_by_id(1)
    assert result == 'encargado'
    mock_Admin.query.get.return_value = 'admin'
    result = repo.get_empleado_by_id(2)
    assert result == 'admin'

@patch('architectural_patterns.repository.empleado_repository.db')
@patch('architectural_patterns.repository.empleado_repository.Administrador')
@patch('architectural_patterns.repository.empleado_repository.Encargado')
def test_create_empleado(mock_Encargado, mock_Admin, mock_db, repo):
    data_admin = {"tipo": "administrador", "nombre": "A"}
    data_enc = {"tipo": "encargado", "nombre": "E"}
    mock_Admin.return_value = MagicMock()
    mock_Encargado.return_value = MagicMock()
    repo.create_empleado(data_admin)
    repo.create_empleado(data_enc)
    assert mock_db.session.add.called
    assert mock_db.session.commit.called

@patch('architectural_patterns.repository.empleado_repository.db')
def test_create_empleado_tipo_invalido(mock_db, repo):
    with pytest.raises(ValueError):
        repo.create_empleado({"tipo": "otro"}) 