from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import Cliente
from database import db
from datetime import datetime
from architectural_patterns.service.user_service import UserService
from models.user import Administrador, Encargado, Usuario
from models.rol import Rol
from database import db
from architectural_patterns.service.propiedad_service import PropiedadService
from architectural_patterns.service.empleado_service import EmpleadoService
from unittest.mock import patch
from functools import wraps
from models.propiedad import Propiedad
from sqlalchemy.sql.expression import func

from architectural_patterns.service.search_service import SearchService





# Crear un Blueprint para las rutas
main = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta principal
@main.route('/')
def index():
    propiedades_random = Propiedad.query.order_by(func.random()).limit(6).all()
    return render_template('index.html', propiedades_random=propiedades_random)

# Ruta de login
@main.route('/login', methods=['GET', 'POST'])
def login():
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

# Ruta de registro
@main.route('/register', methods=['GET', 'POST'])
def registrarse():
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

@main.route('/search', methods=['GET'])
def search_properties():
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
           


# Ruta para mostrar el formulario de nueva propiedad
@main.route('/propiedades/nueva', methods=['GET', 'POST'])
def nueva_propiedad():
    user_rol = session.get('rol')
    if user_rol not in ['superusuario', 'administrador']:
        flash('No tienes permiso para ingresar nuevas propiedades.', 'danger')
        return redirect(url_for('main.index'))
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
            "descripcion": request.form.get('descripcion', ''),
            "reembolsable": 'reembolsable' in request.form,
            "latitud": request.form.get('latitud') or None,
            "longitud": request.form.get('longitud') or None
        }
        if data["latitud"] is not None and data["latitud"] != "":
            try:
                data["latitud"] = float(data["latitud"])
            except ValueError:
                data["latitud"] = None
        if data["longitud"] is not None and data["longitud"] != "":
            try:
                data["longitud"] = float(data["longitud"])
            except ValueError:
                data["longitud"] = None
        if not data["latitud"] or not data["longitud"]:
            flash("Latitud y longitud son obligatorios.", "danger")
            return render_template('nueva_propiedad.html')
        success, message = PropiedadService().crear_propiedad(data)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return render_template('nueva_propiedad.html')
    return render_template('nueva_propiedad.html')

# Ruta para mostrar el formulario de modificar propiedad
@main.route('/propiedades/modificar/<int:id>', methods=['GET', 'POST'])
@login_required
def modificar_propiedad(id):
    user_rol = session.get('rol')
    if user_rol not in ['superusuario', 'administrador']:
        flash('No tienes permiso para modificar propiedades.', 'danger')
        return redirect(url_for('main.index'))
    from models.propiedad import Propiedad
    propiedad = Propiedad.query.get_or_404(id)
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
            "descripcion": request.form.get('descripcion', ''),
            "reembolsable": 'reembolsable' in request.form,
            "latitud": request.form.get('latitud'),
            "longitud": request.form.get('longitud')
        }
        service = PropiedadService()
        success, message = service.update_propiedad(id, data)
        if success:
            flash(message, 'success')
            return redirect(url_for('main.modificar_propiedad', id=id))
        else:
            flash(message, 'danger')
            # Mantener los datos ingresados en el formulario
            propiedad.__dict__.update(data)
    action_url = url_for('main.modificar_propiedad', id=id)
    return render_template('modificar_propiedad.html', propiedad=propiedad, action_url=action_url)

# Ruta para agregar un nuevo empleado (administrador o encargado)
@main.route('/empleados/nuevo', methods=['GET', 'POST'])
def agregar_empleado():
    # Obtener el rol del usuario actual
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

@main.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('main.login'))

@main.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
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

@main.route('/perfil/eliminar', methods=['POST'])
@login_required
def eliminar_cuenta():
    user_service = UserService()
    user_id = session['user_id']
    user_service.eliminar_usuario_logico(user_id)
    session.clear()
    flash('Cuenta eliminada correctamente.', 'success')
    return redirect(url_for('main.login'))

@main.route('/ver-propiedades')
@login_required
def ver_propiedades():
    page = request.args.get('page', 1, type=int)
    ubicacion = request.args.get('ubicacion', '')
    tipo = request.args.get('tipo', '')
    
    # Obtener las propiedades paginadas
    propiedades = Propiedad.query.filter_by(eliminado=False)
    
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

@main.route('/propiedad/<int:id>')
@login_required
def detalle_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    return render_template('detalle_propiedad.html', propiedad=propiedad)

@main.route('/agregar-propiedad')
def agregar_propiedad_redirect():
    return redirect(url_for('main.nueva_propiedad'))

@main.route('/ver-encargados')
@login_required
def ver_encargados():
    user_rol = session.get('rol')
    if user_rol not in ['superusuario', 'administrador']:
        flash('No tienes permiso para ver los encargados.', 'danger')
        return redirect(url_for('main.index'))
    from models.user import Encargado
    encargados = Encargado.query.all()
    return render_template('ver_encargados.html', encargados=encargados)

@main.route('/propiedad/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_propiedad(id):
    user_rol = session.get('rol')
    if user_rol not in ['superusuario', 'administrador']:
        flash('No tienes permiso para eliminar propiedades.', 'danger')
        return redirect(url_for('main.index'))
    from models.propiedad import Propiedad
    propiedad = Propiedad.query.get_or_404(id)
    propiedad.eliminado = True
    from database import db
    db.session.commit()
    flash('Propiedad eliminada correctamente.', 'success')
    return redirect(request.referrer or url_for('main.ver_propiedades'))

@main.route('/ver-administradores')
@login_required
def ver_administradores():
    user_rol = session.get('rol')
    if user_rol not in ['superusuario', 'administrador']:
        flash('No tienes permiso para ver los administradores.', 'danger')
        return redirect(url_for('main.index'))
    from models.user import Administrador
    administradores = Administrador.query.all()
    return render_template('ver_administradores.html', administradores=administradores)

@main.route('/favoritos/agregar/<int:propiedad_id>', methods=['POST'])
@login_required
def agregar_favorito(propiedad_id):
    from models.user import Cliente
    from models.propiedad import Propiedad
    user_id = session.get('user_id')
    user_rol = session.get('rol')
    if user_rol != 'cliente':
        flash('Solo los clientes pueden agregar favoritos.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    cliente = Cliente.query.get(user_id)
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    if propiedad in cliente.favoritos:
        flash('La propiedad ya está en tus favoritos.', 'info')
    else:
        cliente.favoritos.append(propiedad)
        from database import db
        db.session.commit()
        flash('Propiedad guardada en favoritos', 'success')
    return redirect(request.referrer or url_for('main.index'))
