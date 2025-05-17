from models.propiedad import Propiedad
from database import db

class PropiedadRepository:
    def get_all_properties(self):
        return db.session.query(Propiedad).all()
    
    def get_property_by_id(self, id):
        return db.session.query(Propiedad).filter(Propiedad.id == id).first()
    
    def get_properties_by_location(self, location):
        return db.session.query(Propiedad).filter(Propiedad.ubicacion.ilike(f"%{location}%")).all()
    
    def get_properties_by_price(self, min_price, max_price):
        return db.session.query(Propiedad).filter(Propiedad.precio >= min_price, Propiedad.precio <= max_price).all()
    
    def get_properties_by_features(self, features):
        return db.session.query(Propiedad).filter(Propiedad.caracteristicas.contains(features)).all()
    
    def get_properties_by_date(self, start_date, end_date):
        return db.session.query(Propiedad).filter(Propiedad.fecha_inicio >= start_date, Propiedad.fecha_fin <= end_date).all()
    
    def get_properties_by_date_and_price(self, start_date, end_date, min_price, max_price):
        return db.session.query(Propiedad).filter(Propiedad.fecha_inicio >= start_date, Propiedad.fecha_fin <= end_date, Propiedad.precio >= min_price, Propiedad.precio <= max_price).all()
    
    def get_properties_by_date_and_features(self, start_date, end_date, features):
        return db.session.query(Propiedad).filter(Propiedad.fecha_inicio >= start_date, Propiedad.fecha_fin <= end_date, Propiedad.caracteristicas.contains(features)).all()
    
    def get_properties_by_price_and_features(self, min_price, max_price, features):
        return db.session.query(Propiedad).filter(Propiedad.precio >= min_price, Propiedad.precio <= max_price, Propiedad.caracteristicas.contains(features)).all()
    
    def get_properties_by_date_and_price_and_features(self, start_date, end_date, min_price, max_price, features):
        return db.session.query(Propiedad).filter(Propiedad.fecha_inicio >= start_date, Propiedad.fecha_fin <= end_date, Propiedad.precio >= min_price, Propiedad.precio <= max_price, Propiedad.caracteristicas.contains(features)).all()
    
    
    
    
