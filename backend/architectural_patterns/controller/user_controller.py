from flask import  render_template,  redirect, url_for, flash, request
from architectural_patterns.service.user_service import UserService
from flask_mail import Message
from models.user import Administrador, Encargado

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
        return render_template('profile.html', user=user, paises=paises, form_data=form_data)
    
    
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
        # Si la petición viene de la página de favoritos, renderiza la plantilla actualizada
        if request.referrer and 'ver-favoritos' in request.referrer:
            favoritos = cliente.favoritos
            return render_template('favoritos.html', favoritos=favoritos)
        # Si no, redirige como antes
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

    def ver_favoritos(self, session):
        from models.user import Cliente
        user_id = session.get('user_id')
        user_tipo = session.get('rol')
        if user_tipo != 'cliente':
            flash('Solo los clientes pueden ver favoritos.', 'danger')
            return redirect(url_for('main.index'))
        cliente = Cliente.query.get(user_id)
        favoritos = cliente.favoritos
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
