from database import db
from sqlalchemy import inspect

def test_permiso_table_exists(app):
    from models.permiso import Permiso
    with app.app_context():
        Permiso.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'permiso' in inspector.get_table_names()

def test_permiso_columns_exist(app):
    from models.permiso import Permiso
    with app.app_context():
        Permiso.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('permiso')
        column_names = [col['name'] for col in columns]
        assert 'id' in column_names
        assert 'nombre' in column_names

def test_permiso_primary_key(app):
    from models.permiso import Permiso
    with app.app_context():
        Permiso.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('permiso')['constrained_columns']
        assert pk == ['id']