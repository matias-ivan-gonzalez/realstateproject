from database import db

class Reserva(db.Model):
    __tablename__ = 'reserva'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    #estado = db.Column(db.String(50), nullable=False)  ver si hacemos patron state # Ej: 'pendiente', 'confirmada', 'cancelada'
    
    # Claves foráneas
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)

    # Relaciones
    propiedad = db.relationship('Propiedad', back_populates='reservas')
    cliente = db.relationship('Cliente', back_populates='reservas')


    def __repr__(self):
        return f"<Reserva {self.id} de {self.cliente.nombre} para {self.propiedad.direccion}>"