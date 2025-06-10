from operator import or_
from models.ocupacion import Ocupacion
from database import db

class OcupacionRepository:
    def get_propiedades_ocupadas_entre_fechas(self, fecha_inicio, fecha_fin):
        """
        Devuelve los IDs de propiedades que tienen ocupaciones que se solapan
        con el rango [fecha_inicio, fecha_fin).
        """
        subquery = (
            db.session.query(Ocupacion.propiedad_id)
            .filter(
                ~or_(
                    Ocupacion.fecha_fin <= fecha_inicio,
                    Ocupacion.fecha_inicio >= fecha_fin
                )
            )
            .distinct()
        )
        return [r.propiedad_id for r in subquery.all()]
