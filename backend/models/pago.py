from database import db
from datetime import datetime

class Pago(db.Model):
    __tablename__ = 'pago'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monto = db.Column(db.Float, nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)

    # Relación con Reserva
    reserva = db.relationship('Reserva', backref='pagos')

    def __repr__(self):
        return f"<Pago {self.id} - Reserva {self.reserva_id} - Monto {self.monto}>"
