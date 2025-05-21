from database import db
from sqlalchemy import inspect

def test_rol_permiso_table_exists(app):
    from models.rol_permiso import rol_permiso
    with app.app_context():
        rol_permiso.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'rol_permiso' in inspector.get_table_names()

def test_rol_permiso_columns_exist(app):
    from models.rol_permiso import rol_permiso
    with app.app_context():
        rol_permiso.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('rol_permiso')
        column_names = [col['name'] for col in columns]
        assert 'rol_id' in column_names
        assert 'permiso_id' in column_names

def test_rol_permiso_primary_keys(app):
    from models.rol_permiso import rol_permiso
    with app.app_context():
        rol_permiso.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('rol_permiso')['constrained_columns']
        assert set(pk) == {'rol_id', 'permiso_id'}

def test_rol_permiso_foreign_keys(app):
    from models.rol_permiso import rol_permiso
    with app.app_context():
        rol_permiso.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        fks = inspector.get_foreign_keys('rol_permiso')
        fk_columns = {fk['constrained_columns'][0]: (fk['referred_table'], fk['referred_columns'][0]) for fk in fks}
        assert fk_columns['rol_id'] == ('rol', 'id')
        assert fk_columns['permiso_id'] == ('permiso', 'id')