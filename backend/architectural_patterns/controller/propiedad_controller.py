from architectural_patterns.service.propiedad_service import PropiedadService
from models.propiedad import Propiedad
from flask import render_template, redirect, url_for, flash
from datetime import datetime
from flask import session
from models.user import Cliente
import os
from flask import request

class PropiedadController:
    
    def add_propiedad(self, request):
        if request.method == 'POST':
            data = {
                "nombre": request.form.get('nombre'),
                "direccion": request.form.get('direccion'),
                "ubicacion": request.form.get('ubicacion'),
                "precio": request.form.get('precio'),
                "cantidad_habitaciones": request.form.get('cantidad_habitaciones'),
                "limite_personas": request.form.get('limite_personas'),
                "pet_friendly": 'pet_friendly' in request.form,
                "cochera": 'cochera' in request.form,
                "wifi": 'wifi' in request.form,
                "piscina": 'piscina' in request.form,
                "patio_trasero": 'patio_trasero' in request.form,
                "descripcion": request.form.get('descripcion', ''),
                "latitud": request.form.get('latitud'),
                "longitud": request.form.get('longitud'),
                "reembolsable": 'reembolsable' in request.form,
                "eliminado": False
            }
            success, message = PropiedadService().crear_propiedad(data)
            if success:
                # Obtener la propiedad recién creada para obtener su id
                from models.propiedad import Propiedad
                from sqlalchemy import desc
                nueva_prop = Propiedad.query.order_by(desc(Propiedad.id)).first()
                if nueva_prop:
                    img_dir = os.path.join('static', 'img', f'prop{nueva_prop.id}')
                    os.makedirs(img_dir, exist_ok=True)
                flash(message, 'success')
            else:
                flash(message, 'danger')
            return render_template('nueva_propiedad.html')
        return render_template('nueva_propiedad.html')
    
    def update_propiedad(self, id):
        propiedad = Propiedad.query.get_or_404(id)
        action_url = f"/propiedades/modificar/{id}"
        if request.method == 'POST':
            data = {
                "nombre": request.form.get('nombre'),
                "direccion": request.form.get('direccion'),
                "ubicacion": request.form.get('ubicacion'),
                "precio": request.form.get('precio'),
                "cantidad_habitaciones": request.form.get('cantidad_habitaciones'),
                "limite_personas": request.form.get('limite_personas'),
                "pet_friendly": 'pet_friendly' in request.form,
                "cochera": 'cochera' in request.form,
                "wifi": 'wifi' in request.form,
                "piscina": 'piscina' in request.form,
                "patio_trasero": 'patio_trasero' in request.form,
                "descripcion": request.form.get('descripcion', ''),
                "latitud": request.form.get('latitud'),
                "longitud": request.form.get('longitud'),
                "reembolsable": 'reembolsable' in request.form,
                "eliminado": False
            }
            success, message = PropiedadService().update_propiedad(id, data)
            if success:
                flash('Propiedad modificada correctamente.', 'success')
                return redirect(url_for('main.ver_propiedades'))
            else:
                flash(message, 'danger')
                propiedad = Propiedad.query.get_or_404(id)
                return render_template('modificar_propiedad.html', propiedad=propiedad, action_url=action_url)
        return render_template('modificar_propiedad.html', propiedad=propiedad, action_url=action_url)
    
    
    def list_propiedades(self, request,session):
        page = request.args.get('page', 1, type=int)
        ubicacion = request.args.get('ubicacion', '')
        tipo = request.args.get('tipo', '')
    
    # Obtener las propiedades paginadas
        propiedades = Propiedad.query
        propiedades = propiedades.filter(Propiedad.eliminado == False)
    # Aplicar filtros si existen
        if ubicacion:
            propiedades = propiedades.filter(Propiedad.ubicacion.ilike(f'%{ubicacion}%'))
    
    # Si el usuario es encargado, mostrar solo sus propiedades
        if session.get('rol') == 'encargado':
            propiedades = propiedades.filter(Propiedad.encargado_id == session['user_id'])
    # Si el usuario es administrador o superusuario, mostrar todas las propiedades no eliminadas
    # (ya filtrado arriba)
    
    # Ordenar por nombre
        propiedades = propiedades.order_by(Propiedad.nombre)
    
    # Paginar resultados (5 por página)
        propiedades = propiedades.paginate(page=page, per_page=5, error_out=False)
    
        return render_template('properties_list.html', 
                         propiedades=propiedades,
                         ubicacion=ubicacion,
                         tipo=tipo)
        
        
    def get_propiedad(self, id):
        propiedad = Propiedad.query.get_or_404(id)
        user_favoritos = []
        if session.get('rol') == 'cliente':
            cliente = Cliente.query.get(session.get('user_id'))
            if cliente:
                user_favoritos = cliente.favoritos
        return render_template('detalle_propiedad.html', propiedad=propiedad, user_favoritos=user_favoritos, request=request)

    def eliminar_propiedad(self, id):
        propiedad = Propiedad.query.get_or_404(id)
        if propiedad.reservas and len(propiedad.reservas) > 0:
            flash('La propiedad posee una reserva activa. No es posible eliminarla.', 'danger')
            return redirect(url_for('main.ver_propiedades'))
        propiedad.eliminado = True
        propiedad.nombre = f'eliminated_{propiedad.id}'
        from database import db
        db.session.commit()
        flash('Propiedad eliminada correctamente.', 'success')
        return redirect(url_for('main.ver_propiedades'))
    
    def agregar_imagen(self, request, id):
        from models.imagen import Imagen
        from database import db
        propiedad = Propiedad.query.get_or_404(id)
        if request.method == 'POST':
            files = request.files.getlist('imagenes')
            if not files or files[0].filename == '':
                flash('Debes seleccionar al menos una imagen.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=id))
            # Solo permitir .jpg y .png
            files = [f for f in files if f.filename.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not files:
                flash('Solo se permiten archivos .jpg y .png.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=id))
            
            # Verificar si ya existe una entrada para esta carpeta
            carpeta_destino = os.path.join('static', 'img', f'prop{id}')
            carpeta_url = '/static/img/prop' + str(id)
            
            # Crear la carpeta si no existe
            os.makedirs(carpeta_destino, exist_ok=True)
            
            # Guardar las imágenes en la carpeta
            for file in files:
                filename = file.filename
                ruta = os.path.join(carpeta_destino, filename)
                # Si el archivo ya existe, agrega un sufijo incremental
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(ruta):
                    filename = f"{base}_{counter}{ext}"
                    ruta = os.path.join(carpeta_destino, filename)
                    counter += 1
                file.save(ruta)
            
            # Verificar si ya existe una entrada para esta carpeta
            imagen_existente = Imagen.query.filter_by(carpeta=carpeta_url, propiedad_id=id).first()
            if not imagen_existente:
                # Crear una nueva entrada para la carpeta
                imagen = Imagen(carpeta=carpeta_url, propiedad=propiedad)
                db.session.add(imagen)
                db.session.commit()
            
            flash('Las imágenes se han agregado correctamente a la propiedad.', 'success')
            return redirect(url_for('main.detalle_propiedad', id=id))
        return redirect(url_for('main.detalle_propiedad', id=id))
    
    def eliminar_imagen(self, imagen_id):
        from models.imagen import Imagen
        from database import db
        imagen = Imagen.query.get_or_404(imagen_id)
        propiedad_id = imagen.propiedad_id
        # Eliminar carpeta física
        if imagen.carpeta:
            ruta_carpeta = os.path.join(os.getcwd(), imagen.carpeta.lstrip('/').replace('/', os.sep))
            if os.path.exists(ruta_carpeta):
                import shutil
                shutil.rmtree(ruta_carpeta)
        db.session.delete(imagen)
        db.session.commit()
        flash('Carpeta de imágenes eliminada correctamente.', 'success')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    
    def ver_propiedades_asignar(self, session, encargado_id):
        from models.propiedad import Propiedad
        from models.user import Usuario
        encargado = Usuario.query.get_or_404(encargado_id)
        propiedades = Propiedad.query.filter_by(eliminado=False, encargado_id=None).all()
        return render_template('asignar_propiedad.html', encargado=encargado, propiedades=propiedades)

    def ver_propiedades_desasignar(self, session, encargado_id):
        from models.propiedad import Propiedad
        from models.user import Usuario
        encargado = Usuario.query.get_or_404(encargado_id)
        propiedades = Propiedad.query.filter_by(eliminado=False, encargado_id=encargado_id).all()
        return render_template('desasignar_propiedad.html', encargado=encargado, propiedades=propiedades)

    def asignar_propiedad(self, session, propiedad_id, encargado_id):
        from models.propiedad import Propiedad
        from database import db
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        propiedad.encargado_id = encargado_id
        db.session.commit()
        flash('Propiedad asignada correctamente.', 'success')
        return redirect(url_for('main.ver_encargados'))

    def desasignar_propiedad(self, session, propiedad_id):
        from models.propiedad import Propiedad
        from database import db
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        propiedad.encargado_id = None
        db.session.commit()
        flash('Propiedad desasignada correctamente.', 'success')
        return redirect(url_for('main.ver_encargados'))
    
    
    