from database import db
from .rol_permiso import rol_permiso  # Import relativo correcto

class Rol(db.Model):
    __tablename__ = 'rol'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    permisos = db.relationship('Permiso', secondary=rol_permiso, back_populates='roles')
    usuarios = db.relationship('models.user.Usuario', back_populates='rol')
