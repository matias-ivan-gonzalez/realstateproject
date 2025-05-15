from database import db  

rol_permiso = db.Table('rol_permiso',
    db.Column('rol_id', db.Integer, db.ForeignKey('rol.id'), primary_key=True),
    db.Column('permiso_id', db.Integer, db.ForeignKey('permiso.id'), primary_key=True)
)