import os
from flask import render_template, redirect, url_for, flash, request
from database import db
from models.propiedad import Propiedad
from architectural_patterns.service.propiedad_service import PropiedadService
from flask import session
from models.user import Cliente
from flask import request
from sqlalchemy import desc
from config import MERCADOPAGO_PUBLIC_KEY
from models.ocupacion import Ocupacion
from models.reserva import Reserva

class PropiedadController:

    def get_estadisticas_propiedad(self, propiedad_id, mes, anio):
        from models.propiedad import Propiedad
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        service = PropiedadService()
        return propiedad, service.get_estadisticas(propiedad, mes, anio)
    
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
                nueva_prop = Propiedad.query.order_by(desc(Propiedad.id)).first()
                if nueva_prop:
                    img_dir = os.path.join('static', 'img', f'prop{nueva_prop.id}')
                    os.makedirs(img_dir, exist_ok=True)
                flash(message, 'success')
                return render_template('nueva_propiedad.html', form_data={})
            else:
                flash(message, 'danger')
                return render_template('nueva_propiedad.html', form_data=data)
        return render_template('nueva_propiedad.html', form_data={})
    
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
        cliente = None
        if session.get('rol') == 'cliente':
            cliente = Cliente.query.get(session.get('user_id'))
            if cliente:
                user_favoritos = cliente.favoritos

        # Flash message para reserva exitosa SOLO si corresponde
        porcentaje_flash = session.pop('show_reserva_exitosa_flash', None)
        if porcentaje_flash is not None:
            flash(f'Reserva exitosa {porcentaje_flash}% abonado', 'success')
        # Flash message para reserva fallida SOLO si corresponde
        if session.pop('show_reserva_fallida_flash', None):
            flash('Reserva fallida por error en el pago', 'danger')

        # Contar imágenes reales
        total_imagenes = 0
        for imagen in propiedad.imagenes:
            ruta_carpeta = os.path.join(os.getcwd(), imagen.carpeta.lstrip('/').replace('/', os.sep))
            if os.path.exists(ruta_carpeta):
                archivos = [f for f in os.listdir(ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                total_imagenes += len(archivos)

        # Guardar el total de imágenes en la sesión
        session['total_imagenes_reales'] = total_imagenes

        # Obtener fechas ocupadas y reservadas
        fechas_ocupadas = []
        for ocup in propiedad.ocupaciones:
            fechas_ocupadas.append({
                'inicio': ocup.fecha_inicio.strftime('%Y-%m-%d'),
                'fin': ocup.fecha_fin.strftime('%Y-%m-%d')
            })
        from models.user import Usuario
        fechas_reservadas = []
        for res in propiedad.reservas:
            if str(res.estado).lower() in ('futura', 'en_curso'):
                nombre_cliente = "-"
                if res.cliente_id:
                    cliente_obj = Usuario.query.get(res.cliente_id)
                    if cliente_obj:
                        nombre_cliente = f"{cliente_obj.nombre} {cliente_obj.apellido}"
                fechas_reservadas.append({
                    'inicio': res.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': res.fecha_fin.strftime('%Y-%m-%d'),
                    'estado': str(res.estado),
                    'cliente_id': res.cliente_id,
                    'cliente_nombre': nombre_cliente
                })
        # Mostrar días ocupados si es encargado y la propiedad está asignada
        dias_ocupados_encargado = None
        if session.get('rol') == 'encargado' and propiedad.encargado_id == session.get('user_id'):
            from models.ocupacion import Ocupacion
            from datetime import date
            year = date.today().year
            # Solo contar ocupaciones activas en la base de datos, no soft-deleted
            ocupaciones_encargado = Ocupacion.query.filter_by(administrador_id=session.get('user_id'), propiedad_id=propiedad.id).all()
            dias_ocupados = 0
            for ocup in ocupaciones_encargado:
                if ocup.fecha_inicio.year == year and (not hasattr(ocup, 'tipo') or ocup.tipo != 'inhabilitacion'):
                    dias_ocupados += (ocup.fecha_fin - ocup.fecha_inicio).days + 1
            dias_ocupados_encargado = dias_ocupados
        return render_template('detalle_propiedad.html', 
                             propiedad=propiedad, 
                             user_favoritos=user_favoritos, 
                             request=request,
                             total_imagenes_reales=total_imagenes,
                             fechas_ocupadas=fechas_ocupadas,
                             fechas_reservadas=fechas_reservadas,
                             dias_ocupados_encargado=dias_ocupados_encargado,
                             mercadopago_public_key=MERCADOPAGO_PUBLIC_KEY,
                             cliente=cliente)

    def eliminar_propiedad(self, id):
        propiedad = Propiedad.query.get_or_404(id)
        if propiedad.reservas and len(propiedad.reservas) > 0:
            flash('La propiedad posee una reserva activa. No es posible eliminarla.', 'danger')
            return redirect(url_for('main.ver_propiedades'))
        propiedad.eliminado = True
        propiedad.nombre = f'eliminated_{propiedad.id}'
        db.session.commit()
        flash('Propiedad eliminada correctamente.', 'success')
        return redirect(url_for('main.ver_propiedades'))
    
    def agregar_imagen(self, request, id):
        from models.imagen import Imagen
        from database import db
        propiedad = Propiedad.query.get_or_404(id)
        
        if request.method == 'POST':
            # Contar imágenes reales en todas las carpetas de la propiedad
            total_imagenes = 0
            for imagen in propiedad.imagenes:
                ruta_carpeta = os.path.join(os.getcwd(), imagen.carpeta.lstrip('/').replace('/', os.sep))
                if os.path.exists(ruta_carpeta):
                    archivos = [f for f in os.listdir(ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    total_imagenes += len(archivos)

            # Verificar el límite de 5 imágenes
            if total_imagenes >= 5:
                flash('No es posible agregar la cantidad de imágenes seleccionada. El máximo es 5.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=id))
                
            files = request.files.getlist('imagenes')
            if not files or files[0].filename == '':
                flash('Debes seleccionar al menos una imagen.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=id))
            # Solo permitir .jpg y .png
            files = [f for f in files if f.filename.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if not files:
                flash('Solo se permiten archivos .jpg y .png.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=id))
            
            # Verificar que no se exceda el límite con las nuevas imágenes
            if total_imagenes + len(files) > 5:
                flash('No es posible agregar la cantidad de imágenes seleccionada. El máximo es 5.', 'danger')
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
            
            flash('La/las imágenes se ha/han agregado correctamente a la propiedad.', 'success')
            return redirect(url_for('main.detalle_propiedad', id=id))
        return redirect(url_for('main.detalle_propiedad', id=id))
    
    def eliminar_imagen(self, imagen_id):
        from models.imagen import Imagen
        from database import db
        imagen = Imagen.query.get_or_404(imagen_id)
        propiedad_id = imagen.propiedad_id

        # Obtener el nombre del archivo a eliminar de los parámetros
        nombre_archivo = request.args.get('nombre_archivo')
        if not nombre_archivo:
            flash('No se especificó qué imagen eliminar.', 'danger')
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

        # Construir la ruta completa al archivo
        ruta_archivo = os.path.join(os.getcwd(), imagen.carpeta.lstrip('/').replace('/', os.sep), nombre_archivo)
        
        # Verificar si el archivo existe y eliminarlo
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
            flash('Imagen eliminada correctamente.', 'success')
        else:
            flash('No se encontró la imagen especificada.', 'warning')

        # Verificar si quedan más archivos en la carpeta
        ruta_carpeta = os.path.join(os.getcwd(), imagen.carpeta.lstrip('/').replace('/', os.sep))
        archivos_restantes = [f for f in os.listdir(ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        # Si no quedan más imágenes, eliminar la carpeta y el registro
        if not archivos_restantes:
            os.rmdir(ruta_carpeta)
            db.session.delete(imagen)
            db.session.commit()

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
        from models.reserva import Reserva
        from database import db
        from datetime import date
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        # Validar que no haya una reserva en curso en la fecha actual
        hoy = date.today()
        reservas_en_curso = Reserva.query.filter(
            Reserva.propiedad_id == propiedad_id,
            Reserva.fecha_inicio <= hoy,
            Reserva.fecha_fin >= hoy
        ).all()
        if reservas_en_curso:
            flash('No se puede asignar la propiedad porque tiene una reserva en curso.', 'danger')
            return redirect(url_for('main.ver_encargados'))
        propiedad.encargado_id = encargado_id
        db.session.commit()
        flash('Propiedad asignada correctamente.', 'success')
        return redirect(url_for('main.ver_encargados'))

    def desasignar_propiedad(self, session, propiedad_id):
        from models.propiedad import Propiedad
        from models.reserva import Reserva
        from database import db
        from datetime import date
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        # Validar que no haya una reserva en curso en la fecha actual
        hoy = date.today()
        reservas_en_curso = Reserva.query.filter(
            Reserva.propiedad_id == propiedad_id,
            Reserva.fecha_inicio <= hoy,
            Reserva.fecha_fin >= hoy
        ).all()
        if reservas_en_curso:
            flash('No se puede desasignar la propiedad porque tiene una reserva en curso.', 'danger')
            return redirect(url_for('main.ver_encargados'))
        propiedad.encargado_id = None
        db.session.commit()
        flash('Propiedad desasignada correctamente.', 'success')
        return redirect(url_for('main.ver_encargados'))

    def ocupar_propiedad(self, request, session, propiedad_id):
        from models.ocupacion import Ocupacion
        from database import db
        from datetime import datetime, timedelta
        from models.propiedad import Propiedad
        # Permitir a administradores, superusuarios y encargados
        rol = session.get('rol')
        user_id = session.get('user_id')
        if rol not in ['administrador', 'superusuario', 'encargado']:
            flash('No tienes permisos para ocupar una propiedad.', 'danger')
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        # Restricciones para encargado
        if rol == 'encargado':
            if propiedad.encargado_id != user_id:
                flash('Solo puedes ocupar propiedades que tienes asignadas.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
        if request.method == 'POST':
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = request.form.get('fecha_fin')
            if not fecha_inicio or not fecha_fin:
                flash('Debes ingresar ambas fechas.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha inválido.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
            if fecha_fin_dt < fecha_inicio_dt:
                flash('La fecha de fin no puede ser anterior a la de inicio.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
            # Validar solapamiento de ocupaciones
            ocupaciones_existentes = Ocupacion.query.filter_by(propiedad_id=propiedad_id).all()
            for ocup in ocupaciones_existentes:
                if not (fecha_fin_dt < ocup.fecha_inicio or fecha_inicio_dt > ocup.fecha_fin):
                    flash('Ya existe una ocupación en ese rango de fechas.', 'danger')
                    return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
            # Validar solapamiento de reservas futuras/en curso
            reservas_conflictivas = Reserva.query.filter(
                Reserva.propiedad_id == propiedad_id,
                Reserva.fecha_inicio <= fecha_fin_dt,
                Reserva.fecha_fin >= fecha_inicio_dt,
                Reserva.estado.in_(['futura', 'en_curso'])
            ).all()
            if reservas_conflictivas:
                flash('Ya existe una ocupación en ese rango de fechas.', 'danger')
                return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
            # Restricción de 15 días por año para encargados
            if rol == 'encargado':
                year = fecha_inicio_dt.year
                # Cambiado: sumar todas las ocupaciones del encargado en el año, sin importar la propiedad
                ocupaciones_encargado = Ocupacion.query.filter_by(administrador_id=user_id).all()
                dias_ocupados = 0
                for ocup in ocupaciones_encargado:
                    if ocup.fecha_inicio.year == year and (not hasattr(ocup, 'tipo') or ocup.tipo != 'inhabilitacion'):
                        dias_ocupados += (ocup.fecha_fin - ocup.fecha_inicio).days + 1
                dias_nueva_ocupacion = (fecha_fin_dt - fecha_inicio_dt).days + 1
                if dias_ocupados + dias_nueva_ocupacion > 15:
                    flash(f'No puedes ocupar más de 15 días por año.', 'danger')
                    return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
            ocupacion = Ocupacion(
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt,
                administrador_id=user_id,
                propiedad_id=propiedad_id
            )
            db.session.add(ocupacion)
            db.session.commit()
            flash('Ocupación exitosa.', 'success')
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

    def ocupar_propiedad_form(self, request, session, propiedad_id):
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        # Obtener fechas ocupadas y reservadas igual que en get_propiedad
        fechas_ocupadas = []
        for ocup in propiedad.ocupaciones:
            fechas_ocupadas.append({
                'inicio': ocup.fecha_inicio.strftime('%Y-%m-%d'),
                'fin': ocup.fecha_fin.strftime('%Y-%m-%d')
            })
        from models.user import Usuario
        fechas_reservadas = []
        for res in propiedad.reservas:
            if str(res.estado).lower() in ('futura', 'en_curso'):
                fechas_reservadas.append({
                    'inicio': res.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': res.fecha_fin.strftime('%Y-%m-%d'),
                    'estado': str(res.estado),
                    'cliente_id': res.cliente_id
                })
        dias_ocupados_encargado = None
        if session.get('rol') == 'encargado' and propiedad.encargado_id == session.get('user_id'):
            from models.ocupacion import Ocupacion
            from datetime import date
            year = date.today().year
            # Cambiado: sumar todas las ocupaciones del encargado en el año, sin importar la propiedad
            ocupaciones_encargado = Ocupacion.query.filter_by(administrador_id=session.get('user_id')).all()
            dias_ocupados = 0
            for ocup in ocupaciones_encargado:
                if ocup.fecha_inicio.year == year and (not hasattr(ocup, 'tipo') or ocup.tipo != 'inhabilitacion'):
                    dias_ocupados += (ocup.fecha_fin - ocup.fecha_inicio).days + 1
            dias_ocupados_encargado = dias_ocupados
        return render_template('ocupar_propiedad.html',
                              propiedad=propiedad,
                              fechas_ocupadas=fechas_ocupadas,
                              fechas_reservadas=fechas_reservadas,
                              dias_ocupados_encargado=dias_ocupados_encargado,
                              request=request)

    def inhabilitar_propiedad_form(self, request, session, propiedad_id):
        """
        Renderiza el formulario de inhabilitación de propiedad, mostrando fechas ocupadas, reservadas y posibles conflictos.
        """
        from models.propiedad import Propiedad
        from models.reserva import Reserva
        from models.ocupacion import Ocupacion
        from datetime import date
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        hoy = date.today()
        
        # Fechas ocupadas (ocupaciones) con información adicional
        fechas_ocupadas = []
        for ocup in propiedad.ocupaciones:
            fechas_ocupadas.append({
                'inicio': ocup.fecha_inicio.strftime('%Y-%m-%d'), 
                'fin': ocup.fecha_fin.strftime('%Y-%m-%d'),
                'tipo': 'encargado' if hasattr(ocup, 'encargado_id') and getattr(ocup, 'encargado_id', None) else 'admin',
                'fecha_inicio': ocup.fecha_inicio,
                'fecha_fin': ocup.fecha_fin,
                'encargado_id': getattr(ocup, 'encargado_id', None)
            })
        
        # Fechas reservadas (TODAS las reservas, igual que en get_propiedad)
        fechas_reservadas = []
        for res in propiedad.reservas:
            if str(res.estado).lower() in ('futura', 'en_curso'):
                fechas_reservadas.append({
                    'inicio': res.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': res.fecha_fin.strftime('%Y-%m-%d'),
                    'estado': str(res.estado),
                    'cliente_id': res.cliente_id
                })
        
        # Fechas inhabilitadas (ocupaciones de tipo 'inhabilitacion')
        fechas_inhabilitadas = []
        for ocup in propiedad.ocupaciones:
            if getattr(ocup, 'tipo', None) == 'inhabilitacion':
                fechas_inhabilitadas.append({
                    'inicio': ocup.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': ocup.fecha_fin.strftime('%Y-%m-%d')
                })
        
        return render_template(
            'inhabilitar_propiedad.html',
            propiedad=propiedad,
            fechas_ocupadas=fechas_ocupadas,
            fechas_reservadas=fechas_reservadas,
            fechas_inhabilitadas=fechas_inhabilitadas,
            request=request
        )

    def inhabilitar_propiedad(self, propiedad_id, fecha_inicio, fecha_fin, accion_reserva, session):
        """
        Bloquea la propiedad para el rango de fechas indicado.
        Si hay reservas en ese rango, requiere acción (reintegrar/upgrade).
        Si hay ocupaciones de encargado futuras, las elimina y devuelve días.
        Si hay ocupaciones de admin/superuser futuras, las elimina.
        Valida fechas y solapamientos.
        """
        from models.propiedad import Propiedad
        from models.reserva import Reserva
        from models.ocupacion import Ocupacion
        from database import db
        from datetime import datetime, date

        propiedad = Propiedad.query.get_or_404(propiedad_id)
        hoy = date.today()

        # Validación de fechas
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except Exception:
            return False, 'Formato de fecha inválido.', 'danger'
        if fecha_fin_dt < fecha_inicio_dt:
            return False, 'La fecha de fin no puede ser anterior a la de inicio.', 'danger'
        if fecha_inicio_dt < hoy or fecha_fin_dt < hoy:
            return False, 'No se pueden seleccionar fechas anteriores a hoy.', 'danger'

        # Buscar reservas futuras en el rango que se solapen con el rango seleccionado
        reservas_afectadas = Reserva.query.filter(
            Reserva.propiedad_id == propiedad_id,
            Reserva.fecha_inicio <= fecha_fin_dt,
            Reserva.fecha_fin >= fecha_inicio_dt,
            Reserva.estado == 'futura'
        ).all()

        # Buscar ocupaciones en el rango
        ocupaciones_afectadas = Ocupacion.query.filter(
            Ocupacion.propiedad_id == propiedad_id,
            Ocupacion.fecha_inicio <= fecha_fin_dt,
            Ocupacion.fecha_fin >= fecha_inicio_dt
        ).all()

        # Verificar si hay ocupaciones en curso o pasadas que se solapan
        ocupaciones_bloqueantes = []
        ocupaciones_encargado_a_eliminar = []
        ocupaciones_futuras_admin = []
        encargado_id_prop = propiedad.encargado_id
        for ocup in ocupaciones_afectadas:
            # Ocupación en curso: no permitir inhabilitar
            if ocup.fecha_inicio <= hoy <= ocup.fecha_fin:
                ocupaciones_bloqueantes.append(ocup)
            # Ocupación futura de encargado: eliminar si es del encargado asignado y no es de tipo inhabilitacion
            elif ocup.administrador_id == encargado_id_prop and ocup.fecha_inicio > hoy and (not ocup.tipo or ocup.tipo != 'inhabilitacion'):
                ocupaciones_encargado_a_eliminar.append(ocup)
            elif ocup.fecha_fin < hoy:
                ocupaciones_bloqueantes.append(ocup)
            elif ocup.fecha_inicio > hoy:
                ocupaciones_futuras_admin.append(ocup)
        if ocupaciones_bloqueantes:
            return False, 'No se puede inhabilitar la propiedad porque hay una ocupación en curso o pasada en el rango seleccionado.', 'danger'

        # Si hay reservas futuras, requiere acción
        if reservas_afectadas:
            if not accion_reserva:
                return False, 'Debe seleccionar una acción para las reservas afectadas.', 'danger'
            
            if accion_reserva == 'reintegrar':
                # Borrado lógico: marcar reservas afectadas como canceladas
                for reserva in reservas_afectadas:
                    reserva.estado = 'cancelada'
                db.session.commit()
                # Eliminar ocupaciones futuras
                for ocup in ocupaciones_encargado_a_eliminar + ocupaciones_futuras_admin:
                    db.session.delete(ocup)
                # Crear nueva ocupación de inhabilitación
                ocupacion = Ocupacion(
                    fecha_inicio=fecha_inicio_dt,
                    fecha_fin=fecha_fin_dt,
                    administrador_id=session.get('user_id'),
                    propiedad_id=propiedad_id,
                    tipo='inhabilitacion'
                )
                db.session.add(ocupacion)
                db.session.commit()
                return True, 'Propiedad inhabilitada correctamente.', 'success'
                
            elif accion_reserva == 'upgrade':
                # Guardar reservas afectadas en sesión temporal para upgrade
                session['upgrade_reservas'] = [
                    {
                        'id': r.id,
                        'cliente_id': r.cliente_id,
                        'cliente_nombre': f"{r.cliente.nombre} {r.cliente.apellido}",
                        'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'),
                        'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d'),
                        'cantidad_personas': r.cantidad_personas,
                        'propiedad_id': r.propiedad_id
                    } for r in reservas_afectadas
                ]
                session['upgrade_inhabilitacion'] = {
                    'propiedad_id': propiedad_id,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'ocupaciones_encargado': [
                        {
                            'id': o.id,
                            'encargado_id': o.encargado_id,
                            'fecha_inicio': o.fecha_inicio.strftime('%Y-%m-%d'),
                            'fecha_fin': o.fecha_fin.strftime('%Y-%m-%d')
                        } for o in ocupaciones_encargado_a_eliminar
                    ],
                    'ocupaciones_admin': [
                        {
                            'id': o.id,
                            'administrador_id': o.administrador_id,
                            'fecha_inicio': o.fecha_inicio.strftime('%Y-%m-%d'),
                            'fecha_fin': o.fecha_fin.strftime('%Y-%m-%d')
                        } for o in ocupaciones_futuras_admin
                    ]
                }
                return 'upgrade', 'Redirigir a selección de propiedades alternativas', 'info'
            else:
                return False, 'Acción de reserva no válida.', 'danger'

        # Si no hay reservas pero hay ocupaciones de encargado (futuras o en curso), eliminarlas y devolver días
        if ocupaciones_encargado_a_eliminar:
            dias_devueltos = 0
            for ocup in ocupaciones_encargado_a_eliminar:
                dias_ocup = (ocup.fecha_fin - ocup.fecha_inicio).days + 1
                dias_devueltos += dias_ocup
                db.session.delete(ocup)
            for ocup in ocupaciones_futuras_admin:
                db.session.delete(ocup)
            ocupacion = Ocupacion(
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt,
                administrador_id=session.get('user_id'),
                propiedad_id=propiedad_id,
                tipo='inhabilitacion'
            )
            db.session.add(ocupacion)
            db.session.commit()
            return True, f'Propiedad inhabilitada', 'success'

        # Si no hay reservas ni ocupaciones futuras, solo bloquear
        ocupacion = Ocupacion(
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            administrador_id=session.get('user_id'),
            propiedad_id=propiedad_id,
            tipo='inhabilitacion'
        )
        db.session.add(ocupacion)
        db.session.commit()
        return True, 'Propiedad inhabilitada correctamente para el rango seleccionado.', 'success'

    def upgrade_reservas(self, request, session):
        """
        Maneja GET y POST para el flujo de upgrade de reservas afectadas por inhabilitación.
        GET: muestra UI para seleccionar propiedades alternativas.
        POST: procesa la selección y actualiza reservas, elimina ocupaciones, etc.
        """
        from models.reserva import Reserva
        from models.propiedad import Propiedad
        from models.ocupacion import Ocupacion
        from database import db
        from datetime import datetime
        from flask import flash, redirect, url_for, render_template
        
        # --- GET: mostrar selección de propiedades alternativas ---
        if request.method == 'GET':
            reservas = session.get('upgrade_reservas', [])
            inhabilitacion = session.get('upgrade_inhabilitacion', {})
            if not reservas or not inhabilitacion:
                flash('No hay reservas para upgrade.', 'warning')
                return redirect(url_for('main.ver_propiedades'))
            
            alternativas = {}
            for reserva in reservas:
                if session.get('rol') == 'encargado':
                    # Solo mostrar propiedades asignadas al encargado
                    alternativas_reserva = Propiedad.query.filter(
                        Propiedad.eliminado == False,
                        Propiedad.id != reserva['propiedad_id'],
                        Propiedad.encargado_id == session.get('user_id')
                    ).all()
                else:
                    alternativas_reserva = Propiedad.query.filter(
                        Propiedad.eliminado == False,
                        Propiedad.id != reserva['propiedad_id']
                    ).all()
                disponibles = []
                fecha_inicio = datetime.strptime(reserva['fecha_inicio'], '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(reserva['fecha_fin'], '%Y-%m-%d').date()
                for prop in alternativas_reserva:
                    ocupado = False
                    for ocup in prop.ocupaciones:
                        if not (fecha_fin < ocup.fecha_inicio or fecha_inicio > ocup.fecha_fin):
                            ocupado = True
                            break
                    for res in prop.reservas:
                        if res.estado == 'concretada' and not (fecha_fin < res.fecha_inicio or fecha_inicio > res.fecha_fin):
                            ocupado = True
                            break
                    if not ocupado:
                        disponibles.append(prop)
                alternativas[reserva['id']] = disponibles
            
            # Adjuntar propiedades_libres a cada reserva para el template
            for reserva in reservas:
                reserva['propiedades_libres'] = alternativas.get(reserva['id'], [])
            
            # Obtener propiedad_id para el template (usado en el botón Cancelar)
            propiedad_id = inhabilitacion.get('propiedad_id')
            return render_template(
                'upgrade_reserva.html',
                reservas=reservas,
                inhabilitacion=inhabilitacion,
                propiedad_id=propiedad_id
            )
        
        # --- POST: procesar selección de upgrades ---
        elif request.method == 'POST':
            reservas = session.get('upgrade_reservas', [])
            inhabilitacion = session.get('upgrade_inhabilitacion', {})
            if not reservas or not inhabilitacion:
                flash('No hay reservas para upgrade.', 'warning')
                return redirect(url_for('main.ver_propiedades'))
            
            # Recibir selección del formulario: mapping reserva_id -> propiedad_id nueva
            upgrades = {}
            for reserva in reservas:
                key = f'upgrade_{reserva["id"]}'
                nueva_prop_id = request.form.get(key)
                if nueva_prop_id:
                    upgrades[reserva['id']] = int(nueva_prop_id)

            # Procesar upgrades: cancelar reserva original y crear nueva en la propiedad seleccionada
            reservas_procesadas = 0
            for reserva in reservas:
                reserva_obj = Reserva.query.get(reserva['id'])
                # Solo procesar si la reserva no está ya cancelada
                if reserva_obj and reserva_obj.estado != 'cancelada':
                    nueva_prop_id = upgrades.get(reserva['id'])
                    if nueva_prop_id:
                        # Cancelar la reserva original
                        reserva_obj.estado = 'cancelada'
                        db.session.commit()
                        
                        # Crear nueva reserva con los mismos datos pero en la nueva propiedad
                        nueva_reserva = Reserva(
                            fecha_inicio=reserva_obj.fecha_inicio,
                            fecha_fin=reserva_obj.fecha_fin,
                            cantidad_personas=reserva_obj.cantidad_personas,
                            estado='futura',  # Estado correcto para upgrade
                            cliente_id=reserva_obj.cliente_id,
                            propiedad_id=nueva_prop_id
                        )
                        db.session.add(nueva_reserva)
                        db.session.commit()
                        reservas_procesadas += 1
            
            # Eliminar ocupaciones futuras de la propiedad original
            ocupaciones_encargado = inhabilitacion.get('ocupaciones_encargado', [])
            ocupaciones_admin = inhabilitacion.get('ocupaciones_admin', [])
            
            # Eliminar ocupaciones de encargado
            for ocup_data in ocupaciones_encargado:
                ocup = Ocupacion.query.get(ocup_data['id'])
                if ocup:
                    db.session.delete(ocup)
            
            # Eliminar ocupaciones de administrador
            for ocup_data in ocupaciones_admin:
                ocup = Ocupacion.query.get(ocup_data['id'])
                if ocup:
                    db.session.delete(ocup)
            
            # Crear ocupación para bloquear la propiedad original
            prop_id = inhabilitacion.get('propiedad_id')
            fecha_inicio = inhabilitacion.get('fecha_inicio')
            fecha_fin = inhabilitacion.get('fecha_fin')
            
            if prop_id and fecha_inicio and fecha_fin:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                ocupacion = Ocupacion(
                    fecha_inicio=fecha_inicio_dt,
                    fecha_fin=fecha_fin_dt,
                    administrador_id=session.get('user_id'),
                    propiedad_id=prop_id,
                    tipo='inhabilitacion'
                )
                db.session.add(ocupacion)
                db.session.commit()
            
            # Limpiar sesión temporal
            session.pop('upgrade_reservas', None)
            session.pop('upgrade_inhabilitacion', None)
            
            # Mensaje de éxito genérico
            flash('Upgrade exitoso', 'success')
            # Redirigir siempre al detalle de la propiedad inhabilitada
            return redirect(url_for('main.detalle_propiedad', id=prop_id))


