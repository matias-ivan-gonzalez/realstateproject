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


# Crear un Blueprint para las rutas
main = Blueprint('main', __name__)

# Ruta principal
@main.route('/')
def index():
    return render_template('index.html')

# Ruta de login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener datos del formulario o JSON
        if request.is_json:
            email = request.get_json().get('email')
            password = request.get_json().get('password')
        else:
            email = request.form.get('email')
            password = request.form.get('password')

        user_service = UserService()
        user = user_service.authenticate_user(email, password)
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.nombre
            # Guardar el rol del usuario en la sesión
            if isinstance(user, Administrador):
                session['rol'] = 'administrador'
            elif isinstance(user, Encargado):
                session['rol'] = 'encargado'
            else:
                session['rol'] = 'superusuario'

            if request.is_json:
                return {'message': 'Inicio de sesión exitoso', 'rol': session['rol']}, 200
            else:
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('main.index'))
        else:
            if request.is_json:
                return {'error': 'Email o contraseña incorrectos'}, 401
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

# Ruta para mostrar el formulario de nueva propiedad
@main.route('/propiedades/nueva', methods=['GET', 'POST'])
def nueva_propiedad():
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

# Ruta para mostrar el formulario de modificar propiedad
@main.route('/propiedades/modificar', methods=['GET', 'POST'])
def modificar_propiedad():
    # Diccionario de ejemplo con datos de una propiedad
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
        # Obtener datos del formulario o JSON
        if request.is_json:
            data = request.get_json()
        else:
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
            if request.is_json:
                return {'error': 'No tienes permiso para crear un empleado con ese rol'}, 403
            else:
                flash('No tienes permiso para crear un empleado con ese rol', 'danger')
                return render_template('agregar_empleado.html', roles=roles_permitidos, data=data, user_rol=user_rol)
        
        empleado_service = EmpleadoService()
        success, message = empleado_service.crear_empleado(data)
        
        if request.is_json:
            if success:
                return {'message': message}, 200
            else:
                return {'error': message}, 400
        
        if success:
            flash(message, 'success')
            return render_template('agregar_empleado.html', roles=roles_permitidos, user_rol=user_rol)
        else:
            flash(message, 'danger')
            return render_template('agregar_empleado.html', roles=roles_permitidos, data=data, user_rol=user_rol)
            
    return render_template('agregar_empleado.html', roles=roles_permitidos, user_rol=user_rol)

@main.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('main.login'))

@main.route('/check-role')
def check_role():
    if 'user_id' not in session:
        return {'error': 'No hay usuario logueado'}, 401
    return {
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'rol': session.get('rol')
    }