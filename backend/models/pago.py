from database import db
from datetime import datetime

class Pago(db.Model):
    __tablename__ = 'pago'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monto = db.Column(db.Float, nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_cobro_total = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)

    # Relación con Reserva
    reserva = db.relationship('Reserva', backref='pagos')

    def __repr__(self):
        return f"<Pago {self.id} - Reserva {self.reserva_id} - Monto {self.monto} - Status {self.status}>"
