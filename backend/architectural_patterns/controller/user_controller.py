from flask import  render_template,  redirect, url_for, flash
from architectural_patterns.service.user_service import UserService


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
