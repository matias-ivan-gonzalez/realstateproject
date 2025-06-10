from architectural_patterns.repository.propiedad_repository import PropiedadRepository
from architectural_patterns.repository.reserva_repository import ReservaRepository
from architectural_patterns.repository.ocupacion_repository import OcupacionRepository
from datetime import datetime


class SearchService:

    def search_properties(self, data):
        propiedades = []
        repo_prop = PropiedadRepository()
        propiedades = repo_prop.get_properties_by_location(data['ubicacion'])

        if not propiedades:
            return {
                "success": False,
                "mensaje": "No se encontraron propiedades en esta ubicación, pruebe otra ubicación."
            }

        propiedades_disponibles = propiedades
        cantidad_noches = None

    # Filtrar por fechas
        if data['fecha_inicio'] and data['fecha_fin']:
            try:
                fecha_inicio_dt = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
                fecha_fin_dt = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
                cantidad_noches = (fecha_fin_dt - fecha_inicio_dt).days
                if cantidad_noches < 1:
                    cantidad_noches = 1

                repo_res = ReservaRepository()
                repo_ocup = OcupacionRepository()
                propiedades_reservadas_ids = repo_res.get_propiedades_reservadas_entre_fechas(fecha_inicio_dt, fecha_fin_dt)
                propiedades_ocupadas_ids = repo_ocup.get_propiedades_ocupadas_entre_fechas(fecha_inicio_dt, fecha_fin_dt)
                propiedades_no_disponibles = set(propiedades_reservadas_ids) | set(propiedades_ocupadas_ids)
                propiedades_disponibles = [p for p in propiedades_disponibles if p.id not in propiedades_no_disponibles]
            except Exception:
                cantidad_noches = None

        if not propiedades_disponibles:
            return {
                "success": False,
                "mensaje": "No hay propiedades disponibles en esas fechas."
            }

    # Filtrar por características
        propiedades_filtradas_caracteristicas = []
        for propiedad in propiedades_disponibles:
            cumple_caracteristicas = True
            for c in data['caracteristicas']:
                if c == 'wifi' and not propiedad.wifi:
                    cumple_caracteristicas = False
                if c == 'pileta' and not propiedad.piscina:
                    cumple_caracteristicas = False
                if c == 'cochera' and not propiedad.cochera:
                    cumple_caracteristicas = False
                if c == 'mascotas' and not propiedad.pet_friendly:
                    cumple_caracteristicas = False
                if c == 'patio' and not propiedad.patio_trasero:
                    cumple_caracteristicas = False
            if cumple_caracteristicas:
                propiedades_filtradas_caracteristicas.append(propiedad)

        if not propiedades_filtradas_caracteristicas:
            return {
                "success": False,
                "mensaje": "No se encontraron propiedades que cumplan con las características seleccionadas. Intente modificar los filtros."
            }

    # Filtrar por precio
        propiedades_finales = []
        for propiedad in propiedades_filtradas_caracteristicas:
            cumple_min = True
            cumple_max = True
            if data['precio_min']:
                try:
                    cumple_min = propiedad.precio >= float(data['precio_min'])
                except Exception:
                    pass
            if data['precio_max']:
                try:
                    cumple_max = propiedad.precio <= float(data['precio_max'])
                except Exception:
                    pass
            if cumple_min and cumple_max:
                propiedades_finales.append(propiedad)

        if not propiedades_finales:
            return {
                "success": False,
                "mensaje": "No se encontraron propiedades dentro del rango de precios seleccionado. Intente ajustar el rango de precios."
            }

    # Ordenar por precio
        if data.get('orden_precio') == 'asc':
            propiedades_finales.sort(key=lambda p: p.precio)
        elif data.get('orden_precio') == 'desc':
            propiedades_finales.sort(key=lambda p: p.precio, reverse=True)

    # Paginación
        pagina = int(data.get('pagina', 1))
        por_pagina = int(data.get('por_pagina', 3))
        total_propiedades = len(propiedades_finales)
        total_paginas = (total_propiedades + por_pagina - 1) // por_pagina if por_pagina > 0 else 1
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        propiedades_pagina = propiedades_finales[inicio:fin]

        propiedades_serializadas = [
            propiedad.to_dict() if hasattr(propiedad, 'to_dict') else propiedad.__dict__
            for propiedad in propiedades_pagina
        ]

        return {
            "success": True,
            "propiedades": propiedades_serializadas,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": total_paginas,
            "total_propiedades": total_propiedades,
            "mensaje": "",
            "cantidad_noches": None,
            "precios_totales": {}  # Ya no se usa, pero se deja vacío para compatibilidad
        }
