from database import db  


from .Rol_Permiso import rol_permiso


class Permiso(db.Model):
    __tablename__ = 'permiso'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    roles = db.relationship('Rol', secondary=rol_permiso, back_populates='permisos')
