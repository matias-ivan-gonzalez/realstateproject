from flask import  render_template,  redirect, url_for, flash, request
from architectural_patterns.service.user_service import UserService
from flask_mail import Message
from models.user import Administrador, Encargado
from datetime import date, datetime

class UserController:

    def login(self,request, session):
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user_service = UserService()
            user = user_service.authenticate_user(email, password)
            if user:
                session['user_id'] = user.id
                session['user_name'] = user.nombre
                session['email'] = user.email
                # Asignar el rol correctamente
                from models.user import SuperUsuario, Administrador, Encargado, Cliente
                if isinstance(user, SuperUsuario):
                    session['rol'] = 'superusuario'
                elif isinstance(user, Administrador):
                    session['rol'] = 'administrador'
                elif isinstance(user, Encargado):
                    session['rol'] = 'encargado'
                else:
                    session['rol'] = 'cliente'
            # No redirigir inmediatamente, mostrar mensaje y luego redirigir con JS
                flash('Inicio de sesión exitoso.', 'success')
                return render_template('login.html', email=email, login_success=True, redirect_url=url_for('main.index'))
            else:
                flash('Email o contraseña incorrectos.', 'danger')
                return render_template('login.html', email=email)
        return render_template('login.html')
    
    def register(self,request):
        if request.method == 'POST':
            data = {
                'nombre': request.form.get('nombre'),
                'apellido': request.form.get('apellido'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'telefono': request.form.get('telefono'),
                'f_nac': request.form.get('f_nac'),
                'domicilio': request.form.get('domicilio'),
                'nacionalidad': request.form.get('nacionalidad'),
                'dni': request.form.get('dni'),
                'tarjeta': request.form.get('tarjeta')
            }
            user_service = UserService()
            success, message = user_service.register_user(data)
            if success:
                flash(message, 'success')
                return redirect(url_for('main.login'))
            else:
                flash(message, 'danger')
                return render_template('register.html')
        return render_template('register.html')
    
    
    def logout(self,session):
        session.clear()
        flash('Has cerrado sesión.', 'success')
        return redirect(url_for('main.index'))

    
    def profile(self,request,session):
        user_service = UserService()
        user = user_service.get_user_by_id(session['user_id'])      
        if request.method == 'POST':
        # Campos comunes para todos los usuarios
            data = {
                'nombre': request.form.get('nombre'),
                'apellido': request.form.get('apellido'),
                'email': request.form.get('email'),
                'telefono': request.form.get('telefono'),
                'nacionalidad': request.form.get('nacionalidad'),
                'dni': request.form.get('dni'),
                'password': request.form.get('password'),
                'password_confirm': request.form.get('password_confirm')
            }
        # Agregar campos específicos solo si el usuario es cliente
            if user.tipo == 'cliente':
                data.update({
                    'f_nac': request.form.get('f_nac'),
                    'domicilio': request.form.get('domicilio'),
                    'tarjeta': request.form.get('tarjeta')
                })
            success, message = user_service.update_user(session['user_id'], data)
            if success:
                flash(message, 'success')
                return redirect(url_for('main.perfil'))
            else:
                flash(message, 'danger')
                # Mantener los datos ingresados por el usuario en el formulario
                form_data = data.copy()
                if user.tipo == 'cliente':
                    form_data['f_nac'] = data.get('f_nac', '')
                    form_data['domicilio'] = data.get('domicilio', '')
                    form_data['tarjeta'] = data.get('tarjeta', '')
                return render_template('profile.html', user=user, paises=user_service.get_paises(), form_data=form_data)
    # Preparar datos para el formulario
        form_data = {
            'nombre': user.nombre,
            'apellido': user.apellido,
            'email': user.email,
            'telefono': user.telefono,
            'nacionalidad': user.nacionalidad,
            'dni': user.dni
        }
    # Agregar campos específicos de cliente si el usuario es cliente
        if user.tipo == 'cliente':
            form_data.update({
                'f_nac': user.fecha_nacimiento.strftime('%Y-%m-%d') if user.fecha_nacimiento else '',
                'domicilio': user.direccion,
                'tarjeta': user.tarjeta
            })
        paises = user_service.get_paises()
        reservas_activas = user_service.tiene_reservas_activas(session['user_id']) if user.tipo == 'cliente' else False
        return render_template('profile.html', user=user, paises=paises, form_data=form_data, reservas_activas=reservas_activas)
    
    
    def delete_account(self,session):
        user_service = UserService()
        user_id = session['user_id']
        user_service.eliminar_usuario_logico(user_id)
        session.clear()
        flash('Cuenta eliminada correctamente.', 'success')
        return redirect(url_for('main.login'))
    
    
    def recover_password(self,request):
        if request.method == 'POST':
            from app import mail
            email = request.form.get('email')
            user_service = UserService()
            user = user_service.email_exists(email)
            if user:
            # Generar token seguro (esto debe implementarse en UserService)
                token = user_service.generar_token_recuperacion(user)
                enlace = url_for('main.cambiar_contraseña', token=token, _external=True)
                msg = Message('Recuperar contraseña', sender='TU_CORREO@outlook.com', recipients=[email])
                msg.body = f'Para cambiar tu contraseña, haz clic en el siguiente enlace: {enlace}\n\nEste enlace caduca en 1 hora.'
                mail.send(msg)
                flash('Mail enviado', 'success')
            else:
                flash('No existe una cuenta con ese email', 'danger')
            return render_template('recuperar_contraseña.html')
        return render_template('recuperar_contraseña.html')
    
    def change_password(self,request,token):
        user_service = UserService()
        user = user_service.verificar_token_recuperacion(token)
        if not user:
            return render_template('cambiar_contraseña.html', error="Enlace caducado")
        if request.method == 'POST':
            password = request.form.get('password')
            if len(password) < 6:
                return render_template('cambiar_contraseña.html', error="Contraseña invalida, no cumple con el minimo de 6 caracteres")
            user_service.actualizar_password(user, password)
            flash('Contraseña modificada', 'success')
            return redirect(url_for('main.login'))
        return render_template('cambiar_contraseña.html')

    def ver_administradores(self, session):
        user_rol = session.get('rol')
        if user_rol not in ['superusuario', 'administrador']:
            flash('No tienes permiso para ver los administradores.', 'danger')
            return redirect(url_for('main.index'))
        
        page = request.args.get('page', 1, type=int)
        administradores = Administrador.query.filter_by(eliminado=False).order_by(Administrador.nombre).paginate(page=page, per_page=5, error_out=False)
        return render_template('ver_administradores.html', administradores=administradores)

    def ver_encargados(self, session):
        user_rol = session.get('rol')
        if user_rol not in ['superusuario', 'administrador']:
            flash('No tienes permiso para ver los encargados.', 'danger')
            return redirect(url_for('main.index'))
        
        page = request.args.get('page', 1, type=int)
        encargados = Encargado.query.filter_by(eliminado=False).order_by(Encargado.nombre).paginate(page=page, per_page=5, error_out=False)
        return render_template('ver_encargados.html', encargados=encargados)

    def agregar_favorito(self, session, propiedad_id):
        from models.user import Cliente
        from models.propiedad import Propiedad
        from database import db
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo != 'cliente':
            flash('Solo los clientes pueden agregar favoritos.', 'danger')
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
        cliente = Cliente.query.get(user_id)
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        if propiedad not in cliente.favoritos:
            cliente.favoritos.append(propiedad)
            db.session.commit()
            flash('Propiedad agregada a favoritos.', 'success')
        else:
            flash('La propiedad ya está en tus favoritos.', 'info')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

    def quitar_favorito(self, session, propiedad_id):
        from models.user import Cliente
        from models.propiedad import Propiedad
        from database import db
        from flask import request
        if request.method != 'POST':
            return redirect(url_for('main.ver_favoritos'))
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo != 'cliente':
            flash('Solo los clientes pueden quitar favoritos.', 'danger')
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
        cliente = Cliente.query.get(user_id)
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        if propiedad in cliente.favoritos:
            cliente.favoritos.remove(propiedad)
            db.session.commit()
            flash('Propiedad quitada de favoritos.', 'success')
        origen = request.form.get('from')
        if origen == 'detalle':
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
        return redirect(url_for('main.ver_favoritos'))

    def ver_favoritos(self, session):
        from models.user import Cliente
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo != 'cliente':
            flash('Solo los clientes pueden ver favoritos.', 'danger')
            return redirect(url_for('main.index'))
        cliente = Cliente.query.get(user_id)
        favoritos = [p for p in cliente.favoritos if not getattr(p, 'eliminado', False)]
        return render_template('favoritos.html', favoritos=favoritos)

    def eliminar_encargado(self, session, id):
        user_rol = session.get('rol')
        if user_rol not in ['administrador', 'superusuario']:
            flash('No tienes permiso para eliminar encargados.', 'danger')
            return redirect(url_for('main.ver_encargados'))
        from models.user import Encargado
        encargado = Encargado.query.get(id)
        if not encargado:
            flash('Encargado no encontrado.', 'danger')
            return redirect(url_for('main.ver_encargados'))
        if hasattr(encargado, 'propiedades_encargadas') and encargado.propiedades_encargadas:
            if len(encargado.propiedades_encargadas) > 0:
                flash('No es posible eliminar un encargado que tiene propiedades asignadas.', 'danger')
                return redirect(url_for('main.ver_encargados'))
        user_service = UserService()
        success = user_service.eliminar_usuario_logico(id)
        if success:
            flash('Encargado eliminado correctamente.', 'success')
        else:
            flash('No se pudo eliminar el encargado.', 'danger')
        return redirect(url_for('main.ver_encargados'))

    def eliminar_administrador(self, session, id):
        user_rol = session.get('rol')
        if user_rol != 'superusuario':
            flash('No tienes permiso para eliminar administradores.', 'danger')
            return redirect(url_for('main.ver_administradores'))
        user_service = UserService()
        success = user_service.eliminar_usuario_logico(id)
        if success:
            flash('Administrador eliminado correctamente.', 'success')
        else:
            flash('No se pudo eliminar el administrador.', 'danger')
        return redirect(url_for('main.ver_administradores'))

    def cambiar_contrasena_perfil(self, request, session):
        user_service = UserService()
        user = user_service.get_user_by_id(session['user_id'])
        if request.method == 'POST':
            contrasena_actual = request.form.get('contrasena_actual')
            nueva_contrasena = request.form.get('nueva_contrasena')
            # Validar contraseña actual
            if user.contrasena != contrasena_actual:
                flash('La contraseña actual es incorrecta.', 'danger')
                return redirect(url_for('main.perfil'))
            if len(nueva_contrasena) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
                return redirect(url_for('main.perfil'))
            # Ya no se valida que la nueva sea diferente a la actual
            user_service.actualizar_password(user, nueva_contrasena)
            flash('Contraseña modificada', 'success')
            return redirect(url_for('main.perfil'))
        return redirect(url_for('main.perfil'))

    def ver_reservas(self, session):
        from models.user import Cliente
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo != 'cliente':
            flash('Solo los clientes pueden ver sus reservas.', 'danger')
            return redirect(url_for('main.index'))
        cliente = Cliente.query.get(user_id)
        reservas = [r for r in cliente.reservas if getattr(r, 'estado', None) != 'cancelada'] if cliente else []
        current_date = date.today()
        # Pasar una variable para ocultar la columna de acciones
        return render_template('reservas.html', reservas=reservas, current_date=current_date, ocultar_acciones=True)

    def mostrar_formulario_calificacion(self, session, reserva_id):
        from models.reserva import Reserva
        reserva = Reserva.query.get_or_404(reserva_id)
        hoy = date.today()
        dias_diferencia = (hoy - reserva.fecha_fin).days
        # Reglas de negocio
        if reserva.calificacion is not None:
            flash('Esta reserva ya fue calificada.', 'info')
            return redirect(url_for('main.ver_reservas'))
        if hoy <= reserva.fecha_fin:
            flash('Solo puedes calificar una vez finalizada la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        if dias_diferencia > 30:
            flash('Solo puedes calificar hasta 30 días después de la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        return render_template('calificar_propiedad.html', reserva=reserva)

    def procesar_calificacion(self, session, reserva_id, form):
        from models.reserva import Reserva
        from models.calificacion import Calificacion
        from database import db
        reserva = Reserva.query.get_or_404(reserva_id)
        cliente = reserva.cliente
        hoy = date.today()
        dias_diferencia = (hoy - reserva.fecha_fin).days
        # Reglas de negocio
        if reserva.calificacion is not None:
            flash('Esta reserva ya fue calificada.', 'info')
            return redirect(url_for('main.ver_reservas'))
        if hoy <= reserva.fecha_fin:
            flash('Solo puedes calificar una vez finalizada la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        if dias_diferencia > 30:
            flash('Solo puedes calificar hasta 30 días después de la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        estrellas_vista = int(form.get('estrellas_vista'))
        estrellas_ubicacion = int(form.get('estrellas_ubicacion'))
        estrellas_limpieza = int(form.get('estrellas_limpieza'))
        descripcion = form.get('descripcion') or ''
        calificacion = Calificacion(
            reserva_id=reserva.id,
            cliente_id=cliente.id,
            propiedad_id=reserva.propiedad.id,
            estrellas_vista=estrellas_vista,
            estrellas_ubicacion=estrellas_ubicacion,
            estrellas_limpieza=estrellas_limpieza,
            descripcion=descripcion
        )
        db.session.add(calificacion)
        db.session.commit()
        flash('Calificación realizada correctamente!', 'success')
        return redirect(url_for('main.ver_reservas'))

    def mostrar_formulario_editar_calificacion(self, session, calificacion_id):
        from models.calificacion import Calificacion
        from datetime import date
        calificacion = Calificacion.query.get_or_404(calificacion_id)
        reserva = calificacion.reserva
        hoy = date.today()
        dias_diferencia = (hoy - reserva.fecha_fin).days
        if dias_diferencia > 30:
            flash('Solo puedes editar la calificación hasta 30 días después de la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        return render_template('calificar_propiedad.html', reserva=reserva, calificacion=calificacion, editar=True)

    def procesar_edicion_calificacion(self, session, calificacion_id, form):
        from models.calificacion import Calificacion
        from database import db
        from datetime import date
        calificacion = Calificacion.query.get_or_404(calificacion_id)
        reserva = calificacion.reserva
        hoy = date.today()
        dias_diferencia = (hoy - reserva.fecha_fin).days
        if dias_diferencia > 30:
            flash('Solo puedes editar la calificación hasta 30 días después de la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        calificacion.estrellas_vista = int(form.get('estrellas_vista'))
        calificacion.estrellas_ubicacion = int(form.get('estrellas_ubicacion'))
        calificacion.estrellas_limpieza = int(form.get('estrellas_limpieza'))
        calificacion.descripcion = form.get('descripcion') or ''
        db.session.commit()
        flash('Calificación modificada con éxito', 'success')
        return redirect(url_for('main.ver_reservas'))

    def borrar_calificacion(self, session, calificacion_id):
        from models.calificacion import Calificacion
        from database import db
        from datetime import date
        calificacion = Calificacion.query.get_or_404(calificacion_id)
        reserva = calificacion.reserva
        hoy = date.today()
        dias_diferencia = (hoy - reserva.fecha_fin).days
        if dias_diferencia > 30:
            flash('Solo puedes borrar la calificación hasta 30 días después de la estadía.', 'warning')
            return redirect(url_for('main.ver_reservas'))
        db.session.delete(calificacion)
        db.session.commit()
        flash('Calificación borrada exitosamente.', 'success')
        return redirect(url_for('main.ver_reservas'))

    def obtener_lista_reservas(self, session):
        from models.user import Cliente
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo == 'cliente':
            cliente = Cliente.query.get(user_id)
            if cliente:
                return [r for r in cliente.reservas if getattr(r, 'estado', None) != 'cancelada']
            else:
                return []
        return []

    def obtener_reservas_futuras(self, session):
        reservas = self.obtener_lista_reservas(session)
        hoy = datetime.now().date()
        user_id = session.get('user_id')
        from models.conversacion import Conversacion
        futuras = [r for r in reservas if r.fecha_inicio > hoy and getattr(r, 'estado', None) != 'cancelada']
        reservas_serializadas = []
        for r in futuras:
            chat_iniciado_futuro = Conversacion.query.filter_by(reserva_id=r.id, cliente_id=user_id, tipo='futuro', estado='abierta').first() is not None
            reservas_serializadas.append({
                'id': r.id,
                'propiedad': r.propiedad.nombre if r.propiedad else '',
                'direccion': r.propiedad.direccion if r.propiedad else '',
                'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d'),
                'fecha_inicio_obj': r.fecha_inicio,
                'fecha_fin_obj': r.fecha_fin,
                'precio': r.propiedad.precio if r.propiedad else 0,
                'porcentaje_pago_reserva': r.propiedad.porcentaje_pago_reserva if r.propiedad else 0,
                'cantidad_personas': r.cantidad_personas,
                'calificacion': r.calificacion is not None,
                'calificacion_id': r.calificacion.id if r.calificacion else None,
                'fecha_inicio_str': r.fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin_str': r.fecha_fin.strftime('%d/%m/%Y'),
                'chat_iniciado_futuro': chat_iniciado_futuro
            })
        return reservas_serializadas

    def obtener_reservas_concluidas(self, session):
        reservas = self.obtener_lista_reservas(session)
        hoy = datetime.now().date()
        user_id = session.get('user_id')
        from models.conversacion import Conversacion
        concluidas = [r for r in reservas if r.fecha_fin < hoy and (hoy - r.fecha_fin).days > 30]
        reservas_serializadas = []
        for r in concluidas:
            # Cerrar conversaciones si existen y están abiertas
            chat_curso = Conversacion.query.filter_by(reserva_id=r.id, cliente_id=user_id, tipo='curso').first()
            chat_futuro = Conversacion.query.filter_by(reserva_id=r.id, cliente_id=user_id, tipo='futuro').first()
            chat_existio_curso = chat_curso is not None
            chat_existio_futuro = chat_futuro is not None
            conversacion_id_curso = chat_curso.id if chat_curso else None
            conversacion_id_futuro = chat_futuro.id if chat_futuro else None
            # Si la conversación existe y está abierta, cerrarla
            from database import db
            if chat_curso and chat_curso.estado != 'cerrada':
                chat_curso.estado = 'cerrada'
                db.session.commit()
            if chat_futuro and chat_futuro.estado != 'cerrada':
                chat_futuro.estado = 'cerrada'
                db.session.commit()
            reservas_serializadas.append({
                'id': r.id,
                'propiedad': r.propiedad.nombre if r.propiedad else '',
                'direccion': r.propiedad.direccion if r.propiedad else '',
                'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d'),
                'cantidad_personas': r.cantidad_personas,
                'calificacion': r.calificacion is not None,
                'calificacion_id': r.calificacion.id if r.calificacion else None,
                'fecha_inicio_str': r.fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin_str': r.fecha_fin.strftime('%d/%m/%Y'),
                'chat_existio_curso': chat_existio_curso,
                'chat_existio_futuro': chat_existio_futuro,
                'conversacion_id_curso': conversacion_id_curso,
                'conversacion_id_futuro': conversacion_id_futuro
            })
        return reservas_serializadas

    def obtener_calificaciones_pendientes(self, session):
        reservas = self.obtener_lista_reservas(session)
        hoy = datetime.now().date()
        return [r for r in reservas if r.fecha_fin < hoy and (hoy - r.fecha_fin).days <= 30 and r.calificacion is None]

    def obtener_calificaciones_editables(self, session):
        reservas = self.obtener_lista_reservas(session)
        hoy = datetime.now().date()
        return [r for r in reservas if r.fecha_fin < hoy and (hoy - r.fecha_fin).days <= 30 and r.calificacion is not None]

    def obtener_reservas_activas(self, session):
        reservas = self.obtener_lista_reservas(session)
        hoy = datetime.now().date()
        user_id = session.get('user_id')
        from models.conversacion import Conversacion
        activas = [r for r in reservas if r.fecha_inicio <= hoy <= r.fecha_fin]
        reservas_serializadas = []
        for r in activas:
            chat_iniciado_curso = Conversacion.query.filter_by(reserva_id=r.id, cliente_id=user_id, tipo='curso', estado='abierta').first() is not None
            reservas_serializadas.append({
                'id': r.id,
                'propiedad': r.propiedad.nombre if r.propiedad else '',
                'direccion': r.propiedad.direccion if r.propiedad else '',
                'fecha_inicio': r.fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': r.fecha_fin.strftime('%Y-%m-%d'),
                'fecha_inicio_obj': r.fecha_inicio,
                'fecha_fin_obj': r.fecha_fin,
                'precio': r.propiedad.precio if r.propiedad else 0,
                'porcentaje_pago_reserva': r.propiedad.porcentaje_pago_reserva if r.propiedad else 0,
                'cantidad_personas': r.cantidad_personas,
                'calificacion': r.calificacion is not None,
                'calificacion_id': r.calificacion.id if r.calificacion else None,
                'fecha_inicio_str': r.fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin_str': r.fecha_fin.strftime('%d/%m/%Y'),
                'chat_iniciado_curso': chat_iniciado_curso
            })
        return reservas_serializadas

    def ver_pagos_cliente(self, session):
        from models.user import Cliente
        from models.reserva import Reserva
        from models.pago import Pago
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo != 'cliente':
            flash('Solo los clientes pueden ver sus pagos.', 'danger')
            return redirect(url_for('main.index'))
        cliente = Cliente.query.get(user_id)
        reservas = cliente.reservas if cliente else []
        pagos_por_reserva = []
        for reserva in reservas:
            pagos = reserva.pagos  # Relación definida en el modelo
            if pagos:
                pagos_por_reserva.append({
                    'reserva': reserva,
                    'pagos': pagos
                })
        if not pagos_por_reserva:
            return render_template('mis_pagos.html', pagos_por_reserva=None)
        return render_template('mis_pagos.html', pagos_por_reserva=pagos_por_reserva)

    def obtener_reservas_canceladas(self, session):
        reservas = self.obtener_lista_reservas_todas(session)
        canceladas = [r for r in reservas if getattr(r, 'estado', None) == 'cancelada']
        reservas_serializadas = []
        for r in canceladas:
            reservas_serializadas.append({
                'id': r.id,
                'propiedad': r.propiedad.nombre if r.propiedad else '',
                'direccion': r.propiedad.direccion if r.propiedad else '',
                'fecha_inicio': r.fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': r.fecha_fin.strftime('%d/%m/%Y'),
                'cantidad_personas': r.cantidad_personas,
                'estado': r.estado
            })
        return reservas_serializadas

    def obtener_lista_reservas_todas(self, session):
        from models.user import Cliente
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo == 'cliente':
            cliente = Cliente.query.get(user_id)
            if cliente:
                return cliente.reservas
            else:
                return []
        return []
