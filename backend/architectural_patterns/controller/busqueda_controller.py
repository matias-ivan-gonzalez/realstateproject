from flask import render_template, request, redirect, url_for, flash
from architectural_patterns.service.search_service import SearchService



class SearchController:
    
    def search_properties(self, request):
        data = {
        'ubicacion' : request.args.get('ubicacion', ''),
        'fecha_inicio' : request.args.get('fecha_inicio', ''),
        'fecha_fin' : request.args.get('fecha_fin', ''),
        'precio_min' : request.args.get('precio_min', ''),
        'precio_max': request.args.get('precio_max', ''),
        'caracteristicas': request.args.getlist('caracteristicas'),
        'pagina': int(request.args.get('pagina', 1)),
        'por_pagina': 3,
        'orden_precio': request.args.get('orden_precio', '')
        }
        search_service = SearchService()
        resultado = search_service.search_properties(data)

        if resultado['success'] == True:
            return render_template(
                'search_results.html',
                propiedades=resultado['propiedades'],
                pagina=resultado['pagina'],
                por_pagina=resultado['por_pagina'],
                total_paginas=resultado['total_paginas'],
                total_propiedades=resultado['total_propiedades'],
                ubicacion=data['ubicacion'],
                fecha_inicio=data['fecha_inicio'],
                fecha_fin=data['fecha_fin'],
                precio_min=data['precio_min'],
                precio_max=data['precio_max'],
                caracteristicas=data['caracteristicas'],
                cantidad_noches=resultado['cantidad_noches'],
                precios_totales=resultado['precios_totales'],
                mensaje=resultado['mensaje'],
                hide_navbar_search_btn=True,
                orden_precio=data['orden_precio']
            )
        else:
        # Si hay error, resultado es una tupla (False, mensaje)
            mensaje = resultado['mensaje']
            if mensaje == "No se encontraron propiedades disponibles en esta ubicación, pruebe otra ubicación.":
                flash(mensaje, 'danger')    
                return redirect(url_for('main.index'))     
            else:
                flash(mensaje, 'danger')
                return render_template(
                    'search_results.html',
                    propiedades=[],
                    pagina=data['pagina'],
                    por_pagina=data['por_pagina'],
                    total_paginas=0,
                    total_propiedades=0,
                    ubicacion=data['ubicacion'],
                    fecha_inicio=data['fecha_inicio'],
                    fecha_fin=data['fecha_fin'],
                    precio_min=data['precio_min'],
                    precio_max=data['precio_max'],
                    caracteristicas=data['caracteristicas'],
                    cantidad_noches=None,
                    precios_totales={},
                    mensaje=mensaje,
                    hide_navbar_search_btn=True,
                    orden_precio=data['orden_precio']
                )