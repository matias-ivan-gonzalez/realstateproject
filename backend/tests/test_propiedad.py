from database import db
from sqlalchemy import inspect

def test_propiedad_table_exists(app):
    from models.propiedad import Propiedad
    with app.app_context():
        Propiedad.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'propiedad' in inspector.get_table_names()

def test_propiedad_columns_exist(app):
    from models.propiedad import Propiedad
    with app.app_context():
        Propiedad.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('propiedad')
        column_names = [col['name'] for col in columns]
        assert 'id' in column_names
        assert 'nombre' in column_names
        assert 'ubicacion' in column_names
        assert 'precio' in column_names
        assert 'cantidad_habitaciones' in column_names
        assert 'limite_personas' in column_names
        assert 'pet_friendly' in column_names
        assert 'cochera' in column_names
        assert 'wifi' in column_names
        assert 'piscina' in column_names
        assert 'patio_trasero' in column_names
        assert 'descripcion' in column_names
        assert 'superusuario_id' in column_names
        assert 'encargado_id' in column_names

def test_propiedad_primary_key(app):
    from models.propiedad import Propiedad
    with app.app_context():
        Propiedad.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('propiedad')['constrained_columns']
        assert pk == ['id']

def test_propiedad_foreign_keys(app):
    from models.propiedad import Propiedad
    with app.app_context():
        Propiedad.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        fks = inspector.get_foreign_keys('propiedad')
        fk_map = {fk['constrained_columns'][0]: (fk['referred_table'], fk['referred_columns'][0]) for fk in fks}
        assert fk_map['superusuario_id'] == ('usuario', 'id')
        assert fk_map['encargado_id'] == ('usuario', 'id')