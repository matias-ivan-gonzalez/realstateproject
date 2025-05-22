from architectural_patterns.service.propiedad_service import PropiedadService
from models.propiedad import Propiedad
from flask import render_template, redirect, url_for, flash

class PropiedadController:
    
    def add_propiedad(self,request):
        if request.method == 'POST':
            data = {
                "nombre": request.form.get('nombre'),
                "ubicacion": request.form.get('ubicacion'),
                "precio": request.form.get('precio'),
                "cantidad_habitaciones": request.form.get('cantidad_habitaciones'),
                "limite_personas": request.form.get('limite_personas'),
                "pet_friendly": 'pet_friendly' in request.form,
                "cochera": 'cochera' in request.form,
                "wifi": 'wifi' in request.form,
                "piscina": 'piscina' in request.form,
                "patio_trasero": 'patio_trasero' in request.form,
                "descripcion": request.form.get('descripcion', '')
            }
            success, message = PropiedadService().crear_propiedad(data)
            if success:
                flash(message, 'success')
            else:
                flash(message, 'danger')
            return render_template('nueva_propiedad.html')
        return render_template('nueva_propiedad.html')
    
    def update_propiedad(self):
        propiedad = {
            "nombre": "Casa de Prueba",
            "ubicacion": "Calle Falsa 123",
            "precio": 150000,
            "cantidad_habitaciones": 3,
            "limite_personas": 5,
            "pet_friendly": True,
            "cochera": False,
            "wifi": True,
            "piscina": False,
            "patio_trasero": True,
            "descripcion": "Una casa de prueba para modificar."
        }
        action_url = "/propiedades/modificar"
        return render_template('modificar_propiedad.html', propiedad=propiedad, action_url=action_url)
    
    
    def list_propiedades(self, request,session):
        page = request.args.get('page', 1, type=int)
        ubicacion = request.args.get('ubicacion', '')
        tipo = request.args.get('tipo', '')
    
    # Obtener las propiedades paginadas
        propiedades = Propiedad.query
    
    # Aplicar filtros si existen
        if ubicacion:
            propiedades = propiedades.filter(Propiedad.ubicacion.ilike(f'%{ubicacion}%'))
    
    # Si el usuario es encargado, mostrar solo sus propiedades
        if session.get('rol') == 'encargado':
            propiedades = propiedades.filter(Propiedad.encargado_id == session['user_id'])
    # Si el usuario es administrador, mostrar las propiedades que administra
        elif session.get('rol') == 'administrador':
            propiedades = propiedades.filter(Propiedad.administradores.any(id=session['user_id']))
    
    # Ordenar por nombre
        propiedades = propiedades.order_by(Propiedad.nombre)
    
    # Paginar resultados (5 por página)
        propiedades = propiedades.paginate(page=page, per_page=5, error_out=False)
    
        return render_template('properties_list.html', 
                         propiedades=propiedades,
                         ubicacion=ubicacion,
                         tipo=tipo)
        
        
    def get_propiedad(self,id):
        propiedad = Propiedad.query.get_or_404(id)
        return render_template('detalle_propiedad.html', propiedad=propiedad)

    
    
    