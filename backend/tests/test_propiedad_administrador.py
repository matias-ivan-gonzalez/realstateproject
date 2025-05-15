from database import db
from sqlalchemy import inspect

def test_propiedad_administrador_table_exists(app):
    from models.propiedad_administrador import propiedad_administrador
    with app.app_context():
        propiedad_administrador.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'propiedad_administrador' in inspector.get_table_names()

def test_propiedad_administrador_columns_exist(app):
    from models.propiedad_administrador import propiedad_administrador
    with app.app_context():
        propiedad_administrador.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('propiedad_administrador')
        column_names = [col['name'] for col in columns]
        assert 'propiedad_id' in column_names
        assert 'administrador_id' in column_names

def test_propiedad_administrador_primary_keys(app):
    from models.propiedad_administrador import propiedad_administrador
    with app.app_context():
        propiedad_administrador.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('propiedad_administrador')['constrained_columns']
        assert set(pk) == {'propiedad_id', 'administrador_id'}

def test_propiedad_administrador_foreign_keys(app):
    from models.propiedad_administrador import propiedad_administrador
    with app.app_context():
        propiedad_administrador.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        fks = inspector.get_foreign_keys('propiedad_administrador')
        fk_columns = {fk['constrained_columns'][0]: (fk['referred_table'], fk['referred_columns'][0]) for fk in fks}
        assert fk_columns['propiedad_id'] == ('propiedad', 'id')
        assert fk_columns['administrador_id'] == ('usuario', 'id')