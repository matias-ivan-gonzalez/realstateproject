from database import db
from datetime import datetime

class Conversacion(db.Model):
    __tablename__ = 'conversaciones'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    es_futura = db.Column(db.Boolean, default=True)  #TRUE Indica si es una conversación a una reserva futura
    estado = db.Column(db.String(20), default='abierta')

    mensajes = db.relationship('MensajeChat', backref='conversacion', lazy=True)
