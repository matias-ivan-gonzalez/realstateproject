from architectural_patterns.repository.propiedad_repository import PropiedadRepository
from architectural_patterns.repository.reserva_repository import ReservaRepository
from datetime import datetime


class SearchService:

    def search_properties(self, data):
        propiedades = []
        repo_prop = PropiedadRepository()
        propiedades = repo_prop.get_properties_by_location(data['ubicacion'])
        precios_totales = {}
        cantidad_noches = None

        if data['fecha_inicio'] and data['fecha_fin']:
            try:
                fecha_inicio_dt = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
                fecha_fin_dt = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
                cantidad_noches = (fecha_fin_dt - fecha_inicio_dt).days
                if cantidad_noches < 1:
                    cantidad_noches = 1

                repo_res = ReservaRepository()
                propiedades_ocupadas_ids = repo_res.get_propiedades_reservadas_entre_fechas(fecha_inicio_dt, fecha_fin_dt)
                propiedades = [p for p in propiedades if p.id not in propiedades_ocupadas_ids]
            except Exception:
                cantidad_noches = None

        propiedades_filtradas = []
        for propiedad in propiedades:
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
            if not cumple_caracteristicas:
                continue

            if cantidad_noches:
                precio_total = round(propiedad.precio * cantidad_noches, 2)
                precios_totales[propiedad.id] = precio_total

                cumple_min = True
                cumple_max = True
                if data['precio_min']:
                    try:
                        cumple_min = precio_total >= float(data['precio_min'])
                    except Exception:
                        cumple_min = True
                if data['precio_max']:
                    try:
                        cumple_max = precio_total <= float(data['precio_max'])
                    except Exception:
                        cumple_max = True
                if cumple_min and cumple_max:
                    propiedades_filtradas.append(propiedad)
            else:
                precios_totales[propiedad.id] = None
                propiedades_filtradas.append(propiedad)

        # Ordenar por precio si se solicita
        if data.get('orden_precio') == 'asc':
            propiedades_filtradas.sort(key=lambda p: p.precio)
        elif data.get('orden_precio') == 'desc':
            propiedades_filtradas.sort(key=lambda p: p.precio, reverse=True)

        pagina = int(data.get('pagina', 1))
        por_pagina = int(data.get('por_pagina', 3))
        total_propiedades = len(propiedades_filtradas)
        total_paginas = (total_propiedades + por_pagina - 1) // por_pagina if por_pagina > 0 else 1
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        propiedades_pagina = propiedades_filtradas[inicio:fin]

        if data['precio_min'] and data['precio_max'] and total_propiedades == 0:
            return {
                "success": False,
                "mensaje": "No se encontraron propiedades dentro del rango de precios seleccionado. Intente ajustar el rango de precios."
            }
        elif len(propiedades) > 0 and total_propiedades == 0:
            return {
                "success": False,
                "mensaje": "No se encontraron propiedades que cumplan con las caracteristicas seleccionadas. Intente modificar los filtros."
            }
        elif total_propiedades == 0:
            return {
                "success": False,
                "mensaje": "No se encontraron propiedades en esta ubicación, pruebe otra ubicación."
            }

        propiedades_serializadas = [propiedad.to_dict() if hasattr(propiedad, 'to_dict') else propiedad.__dict__ for propiedad in propiedades_pagina]

        return {
            "success": True,
            "propiedades": propiedades_serializadas,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": total_paginas,
            "total_propiedades": total_propiedades,
            "mensaje": "",
            "cantidad_noches": cantidad_noches,
            "precios_totales": precios_totales
        }
