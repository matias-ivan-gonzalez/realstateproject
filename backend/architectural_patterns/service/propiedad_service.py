from architectural_patterns.repository.propiedad_repository import PropiedadRepository
from sqlalchemy import func

class PropiedadService:
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