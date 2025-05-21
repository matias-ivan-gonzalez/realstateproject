from operator import or_
from models.reserva import Reserva
from database import db

class ReservaRepository:
    def get_all_reservas(self):
        return db.session.query(Reserva).all()
    
    def get_reserva_by_id(self, id):
        return db.session.query(Reserva).filter(Reserva.id == id).first()
    
    def get_reservas_by_cliente_id(self, cliente_id):
        return db.session.query(Reserva).filter(Reserva.cliente_id == cliente_id).all()
    
    def get_reservas_by_propiedad_id(self, propiedad_id):
        return db.session.query(Reserva).filter(Reserva.propiedad_id == propiedad_id).all()
    
    def get_reservas_by_date(self, start_date, end_date):
        return db.session.query(Reserva).filter(Reserva.fecha_inicio >= start_date, Reserva.fecha_fin <= end_date).all()

    def get_reservas_by_cliente_and_date(self, cliente_id, start_date, end_date):
        return db.session.query(Reserva).filter(Reserva.cliente_id == cliente_id, Reserva.fecha_inicio >= start_date, Reserva.fecha_fin <= end_date).all()
    
    def get_reservas_by_propiedad_cliente_and_date(self, propiedad_id, cliente_id, start_date, end_date):
        return db.session.query(Reserva).filter(Reserva.propiedad_id == propiedad_id, Reserva.cliente_id == cliente_id, Reserva.fecha_inicio >= start_date, Reserva.fecha_fin <= end_date).all()
    
    def get_propiedades_reservadas_entre_fechas(self, fecha_inicio, fecha_fin):
        """
        Devuelve los IDs de propiedades que tienen reservas que se solapan
        con el rango [fecha_inicio, fecha_fin).
        """
        subquery = (
            db.session.query(Reserva.propiedad_id)
            .filter(
                ~or_(
                    Reserva.fecha_fin <= fecha_inicio,
                    Reserva.fecha_inicio >= fecha_fin
                )
            )
            .distinct()
        )
        return [r.propiedad_id for r in subquery.all()]