import pytest
from datetime import date
from backend.models.reserva import Reserva
from backend.models.propiedad import Propiedad
from backend.models.user import Cliente
from database import db

@pytest.fixture
def sample_cliente(session):
    cliente = Cliente(nombre="Juan Perez", email="juan@test.com")
    session.add(cliente)
    session.commit()
    return cliente

@pytest.fixture
def sample_propiedad(session):
    propiedad = Propiedad(direccion="Calle Falsa 123")
    session.add(propiedad)
    session.commit()
    return propiedad

@pytest.fixture
def session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()

def test_crear_reserva(session, sample_cliente, sample_propiedad):
    reserva = Reserva(
        fecha_inicio=date(2024, 6, 1),
        fecha_fin=date(2024, 6, 10),
        cantidad_personas=4,
        cliente_id=sample_cliente.id,
        propiedad_id=sample_propiedad.id
    )
    session.add(reserva)
    session.commit()
    assert reserva.id is not None
    assert reserva.fecha_inicio == date(2024, 6, 1)
    assert reserva.fecha_fin == date(2024, 6, 10)
    assert reserva.cantidad_personas == 4
    assert reserva.cliente_id == sample_cliente.id
    assert reserva.propiedad_id == sample_propiedad.id

def test_reserva_relationships(session, sample_cliente, sample_propiedad):
    reserva = Reserva(
        fecha_inicio=date(2024, 7, 1),
        fecha_fin=date(2024, 7, 5),
        cantidad_personas=2,
        cliente=sample_cliente,
        propiedad=sample_propiedad
    )
    session.add(reserva)
    session.commit()
    assert reserva.cliente.nombre == "Juan Perez"
    assert reserva.propiedad.direccion == "Calle Falsa 123"

def test_reserva_repr(session, sample_cliente, sample_propiedad):
    reserva = Reserva(
        fecha_inicio=date(2024, 8, 1),
        fecha_fin=date(2024, 8, 3),
        cantidad_personas=1,
        cliente=sample_cliente,
        propiedad=sample_propiedad
    )
    session.add(reserva)
    session.commit()
    expected = f"<Reserva {reserva.id} de {sample_cliente.nombre} para {sample_propiedad.direccion}>"
    assert repr(reserva) == expected