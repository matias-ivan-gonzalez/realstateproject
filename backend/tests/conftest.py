import pytest
from app import create_app
from database import db

@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base de datos en memoria para pruebas
    app.config["SECRET_KEY"] = "test_secret"

    with app.app_context():
        # IMPORTA TODOS LOS MODELOS antes de crear las tablas
        from models.rol import Rol
        from models.permiso import Permiso
        from models.user import Usuario, Cliente, Administrador, Encargado, SuperUsuario
        from models.propiedad import Propiedad
        from models.imagen import Imagen
        from models.propiedad_administrador import propiedad_administrador
        from models.favoritos import favoritos

        db.create_all()  # Ahora sí se crean todas las tablas, incluidas las de asociación

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()