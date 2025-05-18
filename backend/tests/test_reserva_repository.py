import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from architectural_patterns.repository.reserva_repository import ReservaRepository
from models.reserva import Reserva

@pytest.fixture
def mock_db_session(monkeypatch):
    mock_session = MagicMock()
    monkeypatch.setattr('database.db.session', mock_session)
    return mock_session

@pytest.fixture
def reserva_repository():
    return ReservaRepository()

def test_get_all_reservas_returns_all(mock_db_session, reserva_repository):
    reservas = [Reserva(id=1), Reserva(id=2)]
    mock_db_session.query.return_value.all.return_value = reservas
    result = reserva_repository.get_all_reservas()
    assert result == reservas
    mock_db_session.query.assert_called_with(Reserva)

def test_get_reserva_by_id_returns_correct_reserva(mock_db_session, reserva_repository):
    reserva = Reserva(id=1)
    mock_db_session.query.return_value.filter.return_value.first.return_value = reserva
    result = reserva_repository.get_reserva_by_id(1)
    assert result == reserva
    mock_db_session.query.return_value.filter.assert_called()

def test_get_reservas_by_cliente_id_returns_reservas(mock_db_session, reserva_repository):
    reservas = [Reserva(cliente_id=1), Reserva(cliente_id=1)]
    mock_db_session.query.return_value.filter.return_value.all.return_value = reservas
    result = reserva_repository.get_reservas_by_cliente_id(1)
    assert result == reservas

def test_get_reservas_by_propiedad_id_returns_reservas(mock_db_session, reserva_repository):
    reservas = [Reserva(propiedad_id=2)]
    mock_db_session.query.return_value.filter.return_value.all.return_value = reservas
    result = reserva_repository.get_reservas_by_propiedad_id(2)
    assert result == reservas

def test_get_reservas_by_date_returns_reservas(mock_db_session, reserva_repository):
    reservas = [Reserva(fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=1))]
    mock_db_session.query.return_value.filter.return_value.all.return_value = reservas
    result = reserva_repository.get_reservas_by_date(date.today(), date.today() + timedelta(days=1))
    assert result == reservas

def test_get_reservas_by_cliente_and_date_returns_reservas(mock_db_session, reserva_repository):
    reservas = [Reserva(cliente_id=1, fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=1))]
    mock_db_session.query.return_value.filter.return_value.all.return_value = reservas
    result = reserva_repository.get_reservas_by_cliente_and_date(1, date.today(), date.today() + timedelta(days=1))
    assert result == reservas

def test_get_reservas_by_propiedad_cliente_and_date_returns_reservas(mock_db_session, reserva_repository):
    reservas = [Reserva(propiedad_id=2, cliente_id=1, fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=1))]
    mock_db_session.query.return_value.filter.return_value.all.return_value = reservas
    result = reserva_repository.get_reservas_by_propiedad_cliente_and_date(2, 1, date.today(), date.today() + timedelta(days=1))
    assert result == reservas

def test_get_propiedades_reservadas_entre_fechas_returns_ids(mock_db_session, reserva_repository):
    mock_result = [MagicMock(propiedad_id=5), MagicMock(propiedad_id=7)]
    mock_query = MagicMock()
    mock_query.filter.return_value.distinct.return_value.all.return_value = mock_result
    mock_db_session.query.return_value = mock_query

    result = reserva_repository.get_propiedades_reservadas_entre_fechas(date(2024, 1, 1), date(2024, 1, 10))
    assert result == [5, 7]
    mock_db_session.query.assert_called_with(Reserva.propiedad_id)