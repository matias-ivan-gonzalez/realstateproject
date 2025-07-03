from database import db
from .user import SuperUsuario, Administrador, Encargado
from .propiedad_administrador import propiedad_administrador

class Propiedad(db.Model):
    __tablename__ = 'propiedad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad_habitaciones = db.Column(db.Integer, nullable=False)
    limite_personas = db.Column(db.Integer, nullable=False)
    pet_friendly = db.Column(db.Boolean, default=False, nullable=False)
    cochera = db.Column(db.Boolean, default=False, nullable=False)
    wifi = db.Column(db.Boolean, default=False, nullable=False)
    piscina = db.Column(db.Boolean, default=False, nullable=False)
    patio_trasero = db.Column(db.Boolean, default=False, nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    superusuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    encargado_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    reembolsable = db.Column(db.Boolean, default=False, nullable=False)
    eliminado = db.Column(db.Boolean, default=False, nullable=False)
    porcentaje_pago_reserva = db.Column(db.Integer, nullable=False, default=20)  # 0, 20, 100
    
    # Relación con las imágenes
    imagenes = db.relationship('Imagen', back_populates='propiedad', cascade='all, delete-orphan')
    superusuario = db.relationship('SuperUsuario', backref='propiedades', foreign_keys=[superusuario_id])
    administradores = db.relationship('Administrador', secondary=propiedad_administrador, backref='propiedades_administradas')
    encargado = db.relationship('Encargado', backref='propiedades_encargadas', foreign_keys=[encargado_id])

    reservas = db.relationship('Reserva', back_populates='propiedad', cascade='all, delete-orphan')
    ocupaciones = db.relationship('Ocupacion', back_populates='propiedad', cascade='all, delete-orphan')
    calificaciones = db.relationship('Calificacion', back_populates='propiedad', cascade='all, delete-orphan')
    # clientes_favoritos: relación inversa de favoritos, definida en Cliente con backref

    def __repr__(self):
        return f"<Propiedad {self.nombre} - {self.ubicacion}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'ubicacion': self.ubicacion,
            'precio': self.precio,
            'cantidad_habitaciones': self.cantidad_habitaciones,
            'limite_personas': self.limite_personas,
            'pet_friendly': self.pet_friendly,
            'cochera': self.cochera,
            'wifi': self.wifi,
            'piscina': self.piscina,
            'patio_trasero': self.patio_trasero,
            'descripcion': self.descripcion,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'direccion': self.direccion,
            'reembolsable': self.reembolsable,
            'eliminado': self.eliminado,
            'imagenes': [img.to_dict() for img in self.imagenes],
            'promedio_calificacion': self.promedio_calificacion()
        }
    
    def promedio_calificacion(self):
        if not self.calificaciones:
            return None
        total = 0
        for c in self.calificaciones:
            try:
                total += c.promedio_estrellas() 
            except Exception:
                return None
        return round(total / len(self.calificaciones), 2)

    def promedio_limpieza(self):
        if not self.calificaciones:
            return None
        total = 0
        count = 0
        for c in self.calificaciones:
            if c.estrellas_limpieza is not None:
                total += c.estrellas_limpieza
                count += 1
        return round(total / count, 2) if count > 0 else None

    def promedio_ubicacion(self):
        if not self.calificaciones:
            return None
        total = 0
        count = 0
        for c in self.calificaciones:
            if c.estrellas_ubicacion is not None:
                total += c.estrellas_ubicacion
                count += 1
        return round(total / count, 2) if count > 0 else None

    def promedio_vista(self):
        if not self.calificaciones:
            return None
        total = 0
        count = 0
        for c in self.calificaciones:
            if c.estrellas_vista is not None:
                total += c.estrellas_vista
                count += 1
        return round(total / count, 2) if count > 0 else None



