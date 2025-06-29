from database import db
from datetime import datetime

class Conversacion(db.Model):
    __tablename__ = 'conversaciones'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='abierta')
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)  # Relación con reservas
    tipo = db.Column(db.String(20), nullable=False)  # 'futuro' o 'curso'

    mensajes = db.relationship('MensajeChat', backref='conversacion', lazy=True)
