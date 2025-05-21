from database import db

favoritos = db.Table('favoritos',
    db.Column('cliente_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('propiedad_id', db.Integer, db.ForeignKey('propiedad.id'), primary_key=True)
) 