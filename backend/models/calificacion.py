from database import db
from datetime import datetime

class Calificacion(db.Model):
    __tablename__ = 'calificacion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False, unique=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)
    estrellas_vista = db.Column(db.Integer, nullable=False)
    estrellas_ubicacion = db.Column(db.Integer, nullable=False)
    estrellas_limpieza = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    fecha_calificacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    reserva = db.relationship('Reserva', back_populates='calificacion', uselist=False)
    cliente = db.relationship('Cliente', back_populates='calificaciones')
    propiedad = db.relationship('Propiedad', back_populates='calificaciones')

    def __repr__(self):
        return f"<Calificacion {self.id} - Reserva {self.reserva_id}>" 