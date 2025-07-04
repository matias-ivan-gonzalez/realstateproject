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

    def get_reservas_calificables_por_encargado(self, encargado_id, hoy):
        from models.calificacion_cliente import CalificacionCliente
        from models.propiedad import Propiedad
        from sqlalchemy.orm import joinedload
        reservas = (
            db.session.query(Reserva)
            .join(Propiedad)
            .filter(Propiedad.encargado_id == encargado_id)
            .filter(Reserva.estado == 'concretada')
            .options(joinedload(Reserva.cliente), joinedload(Reserva.propiedad))
            .all()
        )
        calificables = []
        for reserva in reservas:
            fecha_limite = reserva.fecha_fin
            if fecha_limite is None:
                continue
            if (hoy > fecha_limite) and ((hoy - fecha_limite).days <= 30):
                ya_calificada = CalificacionCliente.query.filter_by(reserva_id=reserva.id).first()
                if not ya_calificada:
                    calificables.append(reserva)
        return calificables

    def get_reservas_calificaciones_editables_por_encargado(self, encargado_id, hoy):
        from models.calificacion_cliente import CalificacionCliente
        from models.propiedad import Propiedad
        from sqlalchemy.orm import joinedload
        reservas = (
            db.session.query(Reserva)
            .join(Propiedad)
            .filter(Propiedad.encargado_id == encargado_id)
            .filter(Reserva.estado == 'concretada')
            .options(joinedload(Reserva.cliente), joinedload(Reserva.propiedad))
            .all()
        )
        editables = []
        for reserva in reservas:
            fecha_limite = reserva.fecha_fin
            if fecha_limite is None:
                continue
            calif_cliente = CalificacionCliente.query.filter_by(reserva_id=reserva.id).first()
            if calif_cliente and (hoy > fecha_limite) and ((hoy - fecha_limite).days <= 30):
                # Adjuntamos la calificación al objeto reserva para la vista
                reserva.calificacion_cliente = calif_cliente
                editables.append(reserva)
        return editables