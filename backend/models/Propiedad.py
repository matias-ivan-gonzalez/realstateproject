from database import db

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
    
    # Relación con las imágenes
    imagenes = db.relationship('Imagen', back_populates='propiedad', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Propiedad {self.nombre} - {self.ubicacion}>" 