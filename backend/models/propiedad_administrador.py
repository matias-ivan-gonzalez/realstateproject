from database import db

propiedad_administrador = db.Table('propiedad_administrador',
    db.Column('propiedad_id', db.Integer, db.ForeignKey('propiedad.id'), primary_key=True),
    db.Column('administrador_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    extend_existing=True
) 