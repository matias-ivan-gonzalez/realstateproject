from database import db
from models.favoritos import favoritos
from sqlalchemy import inspect

def test_favoritos_table_exists(app):
    with app.app_context():
        # Forzar la creación de la tabla de asociación si no existe
        favoritos.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'favoritos' in inspector.get_table_names()

def test_favoritos_columns_exist(app):
    from sqlalchemy import inspect
    with app.app_context():
        inspector = inspect(db.engine)
        columns = inspector.get_columns('favoritos')
        column_names = [col['name'] for col in columns]
        assert 'cliente_id' in column_names
        assert 'propiedad_id' in column_names

def test_favoritos_primary_keys(app):
    from sqlalchemy import inspect
    with app.app_context():
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('favoritos')['constrained_columns']
        assert set(pk) == {'cliente_id', 'propiedad_id'}

def test_favoritos_foreign_keys(app):
    from sqlalchemy import inspect
    with app.app_context():
        inspector = inspect(db.engine)
        fks = inspector.get_foreign_keys('favoritos')
        fk_columns = {fk['constrained_columns'][0]: (fk['referred_table'], fk['referred_columns'][0]) for fk in fks}
        assert fk_columns['cliente_id'] == ('usuario', 'id')
        assert fk_columns['propiedad_id'] == ('propiedad', 'id')
