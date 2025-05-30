from database import db

class Imagen(db.Model):
    __tablename__ = 'imagen'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carpeta = db.Column(db.String(500), nullable=False)  # Ruta a la carpeta de imágenes
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)
    
    # Relación con la propiedad
    propiedad = db.relationship('Propiedad', back_populates='imagenes')

    def __repr__(self):
        return f"<Imagen carpeta {self.carpeta} de Propiedad {self.propiedad_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'carpeta': self.carpeta,
            'propiedad_id': self.propiedad_id
        }