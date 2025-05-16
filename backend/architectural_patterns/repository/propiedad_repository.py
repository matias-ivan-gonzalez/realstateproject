from models.propiedad import Propiedad
from database import db

class PropiedadRepository:
    @staticmethod
    def get_by_nombre(nombre):
        return Propiedad.query.filter_by(nombre=nombre).first()
    @staticmethod
    def crear_propiedad(data):
        propiedad = Propiedad(**data)
        db.session.add(propiedad)
        db.session.commit()
        return propiedad