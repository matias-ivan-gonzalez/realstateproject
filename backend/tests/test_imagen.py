from database import db
from sqlalchemy import inspect

def test_imagen_table_exists(app):
    from models.imagen import Imagen
    with app.app_context():
        Imagen.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'imagen' in inspector.get_table_names()

def test_imagen_columns_exist(app):
    from models.imagen import Imagen
    with app.app_context():
        Imagen.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('imagen')
        column_names = [col['name'] for col in columns]
        assert 'id' in column_names
        assert 'url' in column_names
        assert 'nombre_archivo' in column_names
        assert 'propiedad_id' in column_names

def test_imagen_primary_key(app):
    from models.imagen import Imagen
    with app.app_context():
        Imagen.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('imagen')['constrained_columns']
        assert pk == ['id']

def test_imagen_foreign_key(app):
    from models.imagen import Imagen
    with app.app_context():
        Imagen.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        fks = inspector.get_foreign_keys('imagen')
        assert any(
            fk['constrained_columns'] == ['propiedad_id'] and fk['referred_table'] == 'propiedad'
            for fk in fks
        )