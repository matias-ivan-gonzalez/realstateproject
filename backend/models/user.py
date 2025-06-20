from database import db  
from .favoritos import favoritos
from .calificacion import Calificacion

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    tipo = db.Column(db.String(50))  # STI: cliente, administrador, etc.
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    nacionalidad = db.Column(db.String(50), nullable=False)
    eliminado = db.Column(db.Boolean, default=False, nullable=False)
    
    # Índice único compuesto para dni y nacionalidad
    __table_args__ = (
        db.UniqueConstraint('dni', 'nacionalidad', name='uix_dni_nacionalidad'),
    )
    
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))

    rol = db.relationship('Rol', back_populates='usuarios')

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': tipo
    }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.nombre} {self.apellido}>"

class Cliente(Usuario):
  
    tarjeta = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    reservas = db.relationship("Reserva", back_populates="cliente", cascade="all, delete-orphan")
    calificaciones = db.relationship('Calificacion', back_populates='cliente', cascade='all, delete-orphan')

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
