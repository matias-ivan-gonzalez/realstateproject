from database import db

class Imagen(db.Model):
    __tablename__ = 'imagen'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(500), nullable=False)  # URL o ruta al archivo de imagen
    nombre_archivo = db.Column(db.String(255), nullable=False)  # Nombre original del archivo
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)
    
    # Relación con la propiedad
    propiedad = db.relationship('Propiedad', back_populates='imagenes')

    def __repr__(self):
        return f"<Imagen {self.nombre_archivo} de Propiedad {self.propiedad_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'nombre_archivo': self.nombre_archivo,
            'propiedad_id': self.propiedad_id
        }