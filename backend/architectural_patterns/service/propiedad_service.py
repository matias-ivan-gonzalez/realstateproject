from architectural_patterns.repository.propiedad_repository import PropiedadRepository
from sqlalchemy import func

class PropiedadService:

    def get_estadisticas(self, propiedad, mes, anio):
        from datetime import date
        reservas = propiedad.reservas
        # Filtrar reservas del mes/año
        reservas_mes = [r for r in reservas if r.fecha_inicio.month == mes and r.fecha_inicio.year == anio]
        reservas_concretadas = len([r for r in reservas_mes if r.estado == 'concretada'])
        reservas_canceladas = len([r for r in reservas_mes if r.estado == 'cancelada'])
        total_dias = sum((r.fecha_fin - r.fecha_inicio).days + 1 for r in reservas_mes if r.estado == 'concretada')
        promedio_dias_reserva = round(total_dias / reservas_concretadas, 2) if reservas_concretadas else 0
        # Porcentaje de ocupación mensual
        dias_mes = (date(anio, mes % 12 + 1, 1) - date(anio, mes, 1)).days if mes < 12 else 31
        porcentaje_ocupacion = round((total_dias / dias_mes) * 100, 2) if dias_mes else 0
        ingresos_estimados = round(total_dias * propiedad.precio, 2)

        # Estadísticas anuales
        reservas_anio_list = [r for r in reservas if r.fecha_inicio.year == anio]
        reservas_anio_concretadas = len([r for r in reservas_anio_list if r.estado == 'concretada'])
        reservas_anio_canceladas = len([r for r in reservas_anio_list if r.estado == 'cancelada'])
        total_dias_anio = sum((r.fecha_fin - r.fecha_inicio).days + 1 for r in reservas_anio_list if r.estado == 'concretada')
        promedio_dias_reserva_anio = round(total_dias_anio / reservas_anio_concretadas, 2) if reservas_anio_concretadas else 0
        dias_anio = 366 if ((anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)) else 365
        porcentaje_ocupacion_anio = round((total_dias_anio / dias_anio) * 100, 2) if dias_anio else 0
        ingresos_estimados_anio = round(total_dias_anio * propiedad.precio, 2)

        return {
            'reservas_concretadas': reservas_concretadas,
            'reservas_canceladas': reservas_canceladas,
            'promedio_dias_reserva': promedio_dias_reserva,
            'porcentaje_ocupacion': porcentaje_ocupacion,
            'ingresos_estimados': ingresos_estimados,
            'reservas_anio_concretadas': reservas_anio_concretadas,
            'reservas_anio_canceladas': reservas_anio_canceladas,
            'promedio_dias_reserva_anio': promedio_dias_reserva_anio,
            'porcentaje_ocupacion_anio': porcentaje_ocupacion_anio,
            'ingresos_estimados_anio': ingresos_estimados_anio
        }
    def __init__(self, repository=None):
        self.repository = repository or PropiedadRepository

    def crear_propiedad(self, data):
        # Normalizar el nombre
        nombre_normalizado = data["nombre"].strip().lower()
        # Validación de campos obligatorios
        required_fields = [
            "nombre", "ubicacion", "precio", "cantidad_habitaciones", "limite_personas", "latitud", "longitud"
        ]
        for field in required_fields:
            if not data.get(field):
                return False, f"El campo {field} es obligatorio."

        # Validación de tipos y valores
        try:
            data["precio"] = float(data["precio"])
            data["cantidad_habitaciones"] = int(data["cantidad_habitaciones"])
            data["limite_personas"] = int(data["limite_personas"])
        except ValueError:
            return False, "Precio, cantidad de habitaciones y límite de personas deben ser numéricos."

        # Validación de unicidad del nombre usando el repository
        if self.repository.get_by_nombre(nombre_normalizado):
            return False, "Ya existe una propiedad con ese nombre."

        # Guardar en la base de datos
        try:
            self.repository.crear_propiedad(data)
            return True, "Propiedad guardada exitosamente."
        except Exception as e:
            if "UNIQUE constraint failed: propiedad.nombre" in str(e):
                return False, "Ya existe una propiedad con ese nombre."
            return False, f"Error al guardar la propiedad: {str(e)}"

    def update_propiedad(self, propiedad_id, data):
        # Normalizar el nombre
        nombre_normalizado = data["nombre"].strip().lower()
        # Validar campos obligatorios (igual que en crear_propiedad)
        required_fields = [
            "nombre", "ubicacion", "precio", "cantidad_habitaciones", "limite_personas", "latitud", "longitud"
        ]
        for field in required_fields:
            if not data.get(field):
                return False, f"El campo {field} es obligatorio."
        # Validar tipos
        try:
            data["precio"] = float(data["precio"])
            data["cantidad_habitaciones"] = int(data["cantidad_habitaciones"])
            data["limite_personas"] = int(data["limite_personas"])
        except ValueError:
            return False, "Precio, cantidad de habitaciones y límite de personas deben ser numéricos."
        # Validar unicidad de nombre (excepto para sí misma)
        existente = self.repository.get_by_nombre(nombre_normalizado)
        if existente and existente.id != propiedad_id:
            return False, "Nombre de la propiedad existente."
        # Llama al repository
        return self.repository.update_propiedad(propiedad_id, data)