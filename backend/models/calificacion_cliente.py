from database import db
from datetime import datetime

class CalificacionCliente(db.Model):
    __tablename__ = 'calificacion_cliente'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False, unique=True)
    encargado_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    opinion = db.Column(db.String(500), nullable=False)
    fecha_calificacion = db.Column(db.DateTime, default=datetime.utcnow)
    reserva = db.relationship('Reserva', backref=db.backref('calificacion_cliente', uselist=False))

    def __repr__(self):
        return f"<CalificacionCliente {self.id} - Reserva {self.reserva_id}>" 