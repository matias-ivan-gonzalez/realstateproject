import architectural_patterns.service.propiedad_service as PropiedadService

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
    
    def update_propiedad(self, propiedad, action_url):
        return render_template('modificar_propiedad.html', propiedad=propiedad, action_url=action_url)
    
    
    