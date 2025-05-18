from database import db  
from .favoritos import favoritos

class Usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    tipo = db.Column(db.String(50))  # STI: cliente, administrador, etc.
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    nacionalidad = db.Column(db.String(50), nullable=False)
    
    
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))

    rol = db.relationship('Rol', back_populates='usuarios')

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': tipo
    }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.nombre} {self.apellido}>"

class Cliente(Usuario):
    reservas = db.relationship("models.reserva.Reserva", back_populates="cliente", cascade="all, delete-orphan")

    favoritos = db.relationship('Propiedad', secondary=favoritos, backref='clientes_favoritos')
    __mapper_args__ = {
        'polymorphic_identity': 'cliente',
    }

class Administrador(Usuario):
    __mapper_args__ = {
        'polymorphic_identity': 'administrador',
    }

class Encargado(Usuario):
    __mapper_args__ = {
        'polymorphic_identity': 'encargado',
    }

class SuperUsuario(Usuario):
    __mapper_args__ = {
        'polymorphic_identity': 'superusuario',
    }
