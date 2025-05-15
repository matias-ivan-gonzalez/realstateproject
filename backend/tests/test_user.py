from database import db
from sqlalchemy import inspect

def test_usuario_table_exists(app):
    from models.user import Usuario
    with app.app_context():
        Usuario.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        assert 'usuario' in inspector.get_table_names()

def test_usuario_columns_exist(app):
    from models.user import Usuario
    with app.app_context():
        Usuario.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        columns = inspector.get_columns('usuario')
        column_names = [col['name'] for col in columns]
        assert 'id' in column_names
        assert 'tipo' in column_names
        assert 'nombre' in column_names
        assert 'apellido' in column_names
        assert 'dni' in column_names
        assert 'email' in column_names
        assert 'contrasena' in column_names
        assert 'telefono' in column_names
        assert 'nacionalidad' in column_names
        assert 'rol_id' in column_names

def test_usuario_primary_key(app):
    from models.user import Usuario
    with app.app_context():
        Usuario.__table__.create(bind=db.engine, checkfirst=True)
        inspector = inspect(db.engine)
        pk = inspector.get_pk_constraint('usuario')['constrained_columns']
        assert pk == ['id']

def test_usuario_repr():
    from models.user import Usuario
    usuario = Usuario(nombre='Juan', apellido='Pérez')
    resultado = repr(usuario)
    assert resultado == "<Usuario Juan Pérez>"