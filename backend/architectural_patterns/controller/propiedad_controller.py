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

        # Obtener la carpeta de imágenes desde nombre_archivo del primer registro de imagen
        imagenes_files = []
        if propiedad.imagenes and propiedad.imagenes[0].nombre_archivo:
            folder = propiedad.imagenes[0].nombre_archivo.replace('\\', '/').replace('static/', '').lstrip('/')
            folder_path = os.path.join('static', folder)
            if os.path.isdir(folder_path):
                for fname in os.listdir(folder_path):
                    if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        imagenes_files.append(f"{folder}/{fname}")

        return render_template('detalle_propiedad.html', propiedad=propiedad, user_favoritos=user_favoritos, imagenes_files=imagenes_files, request=request)

    def eliminar_propiedad(self, id):
        propiedad = Propiedad.query.get_or_404(id)
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
            if len(propiedad.imagenes) + len(files) > 10:
                flash('No puedes tener más de 10 imágenes por propiedad.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=id))
            carpeta_destino = 'static/img/propiedades/'
            for file in files:
                filename = file.filename
                ruta = os.path.join(carpeta_destino, filename)
                file.save(ruta)
                imagen = Imagen(url='/' + ruta.replace('\\', '/'), nombre_archivo=filename, propiedad=propiedad)
                db.session.add(imagen)
            db.session.commit()
            flash('Imágenes agregadas correctamente.', 'success')
            return redirect(url_for('main.detalle_propiedad', id=id))
        return redirect(url_for('main.detalle_propiedad', id=id))
    
    def eliminar_imagen(self, imagen_id):
        from models.imagen import Imagen
        from database import db
        imagen = Imagen.query.get_or_404(imagen_id)
        propiedad_id = imagen.propiedad_id
        # Eliminar archivo físico
        if imagen.url:
            ruta_archivo = os.path.join(os.getcwd(), imagen.url.lstrip('/').replace('/', os.sep))
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
        db.session.delete(imagen)
        db.session.commit()
        flash('Imagen eliminada correctamente.', 'success')
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
    
    
    