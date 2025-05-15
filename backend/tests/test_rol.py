from database import db
from sqlalchemy import inspect

def test_rol_table_exists(app):
    from models.rol import Rol
    with app.app_context():
        Rol.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'rol' in inspector.get_table_names()

def test_rol_columns_exist(app):
    from models.rol import Rol
    with app.app_context():
        Rol.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('rol')
        column_names = [col['name'] for col in columns]
        assert 'id' in column_names
        assert 'nombre' in column_names

def test_rol_primary_key(app):
    from models.rol import Rol
    with app.app_context():
        Rol.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('rol')['constrained_columns']
        assert pk == ['id']