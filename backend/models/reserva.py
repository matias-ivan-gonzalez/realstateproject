from database import db

class Reserva(db.Model):
    __tablename__ = 'reserva'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='futura')  # Ej: 'futura', 'concretada', 'cancelada'
    reembolsable = db.Column(db.Boolean, nullable=False, default=False)
    checkout_realizado = db.Column(db.Boolean, nullable=False, default=False)
    checkout_estado = db.Column(db.String(255), nullable=True)  # Ej: 'pendiente', 'en proceso', 'completado', etc.

    # Claves foráneas
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)

    # Relaciones
    propiedad = db.relationship('Propiedad', back_populates='reservas')
    cliente = db.relationship('Cliente', back_populates='reservas')
    calificacion = db.relationship('Calificacion', back_populates='reserva', uselist=False)
    

    def __repr__(self):
        return f"<Reserva {self.id} de {self.cliente.nombre} para {self.propiedad.direccion}>"