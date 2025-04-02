import pytest
from app import create_app
from database import db
from models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
        db.session.rollback()

def test_create_user(db_session):
    user = User(username='testuser', email='test@example.com')
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = User.query.filter_by(username='testuser').first()
    assert retrieved_user is not None
    assert retrieved_user.email == 'test@example.com'

def test_user_repr():
    user = User(username='sampleuser', email='sample@example.com')
    assert repr(user) == '<User sampleuser>'