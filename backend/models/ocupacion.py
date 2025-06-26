from database import db

class Ocupacion(db.Model):
    __tablename__ = 'ocupacion'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    administrador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)

    administrador = db.relationship('Administrador', backref='ocupaciones')
    propiedad = db.relationship('Propiedad', back_populates='ocupaciones')

    def __repr__(self):
        return f"<Ocupacion {self.id} - Propiedad {self.propiedad_id} por Admin {self.administrador_id}>"
