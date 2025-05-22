from flask import  render_template,  redirect, url_for, flash
from architectural_patterns.service.empleado_service import EmpleadoService
from models.propiedad import Propiedad

class EmpleadoController:
    
    def add_empleado(self, session, request):
        
        user_rol = session.get('rol')
    
    # Definir los roles permitidos según el rol del usuario
        if user_rol == 'superusuario':
            roles_permitidos = ['Administrador', 'Encargado']
        else:
            roles_permitidos = ['Encargado']
    
        if request.method == 'POST':
        # Obtener datos solo del formulario
            data = {
                'nombre': request.form.get('nombre'),
                'apellido': request.form.get('apellido'),
                'dni': request.form.get('dni'),
                'telefono': request.form.get('telefono'),
                'nacionalidad': request.form.get('nacionalidad'),
                'email': request.form.get('email'),
                'contrasena': request.form.get('contrasena'),
                'rol': request.form.get('rol')
            }
        
        # Validar que el rol seleccionado está permitido
            if data['rol'] not in roles_permitidos:
                flash('No tienes permiso para crear un empleado con ese rol', 'danger')
                return render_template('agregar_empleado.html', roles=roles_permitidos, data=data, user_rol=user_rol)
        
            empleado_service = EmpleadoService()
            success, message = empleado_service.crear_empleado(data)
        
            if success:
                flash(message, 'success')
                return redirect(url_for('main.agregar_empleado'))
            else:
                flash(message, 'danger')
                return render_template('agregar_empleado.html', roles=roles_permitidos, data=data, user_rol=user_rol)
            
        return render_template('agregar_empleado.html', roles=roles_permitidos, user_rol=user_rol)
    
    def list_my_propiedades(self, request, current_user):
        # Verificar que el usuario es un encargado
        if not hasattr(current_user, 'propiedades_encargadas'):
            return "Acceso no autorizado", 403
    
    # Obtener el número de página de la URL, por defecto 1
        page = request.args.get('page', 1, type=int)
    # Obtener el filtro de ubicación
        ubicacion = request.args.get('ubicacion', '')
    
    # Consulta base
        query = Propiedad.query.filter_by(encargado_id=current_user.id)
    
    # Aplicar filtro de ubicación si existe
        if ubicacion:
            query = query.filter(Propiedad.ubicacion.ilike(f'%{ubicacion}%'))
    
    # Paginar los resultados
        propiedades = query.paginate(page=page, per_page=10, error_out=False)
    
        return render_template('encargado/mis_propiedades.html', propiedades=propiedades) 