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
from functools import wraps


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
    return render_template('index.html')

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
    roles_permitidos = ['Administrador', 'Encargado']  # Por ahora, ambos
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        dni = request.form.get('dni')
        telefono = request.form.get('telefono')
        nacionalidad = request.form.get('nacionalidad')
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')
        rol_seleccionado = request.form.get('rol')
        from models.rol import Rol
        rol_db = Rol.query.filter_by(nombre=rol_seleccionado.lower()).first()
        # Validaciones
        errores = []
        limpiar = {}
        if len(contrasena) < 6:
            errores.append('Registro fallido. La contraseña debe tener 6 caracteres como minimo')
            limpiar['contrasena'] = True
        existente_dni = Usuario.query.filter_by(dni=dni).first()
        if existente_dni:
            errores.append('Registro fallido. El dni ingresado ya se encuentra registrado')
            limpiar['dni'] = True
        existente_email = Usuario.query.filter_by(email=email).first()
        if existente_email:
            errores.append('Registro fallido. El mail ingresado ya se encuentra registrado')
            limpiar['email'] = True
        if errores:
            for err in errores:
                flash(err, 'danger')
            # Limpiar solo los campos con error
            data = {
                'nombre': nombre,
                'apellido': apellido,
                'dni': '' if limpiar.get('dni') else dni,
                'telefono': telefono,
                'nacionalidad': nacionalidad,
                'email': '' if limpiar.get('email') else email,
                'contrasena': '' if limpiar.get('contrasena') else contrasena,
                'rol': rol_seleccionado
            }
            return render_template('agregar_empleado.html', roles=roles_permitidos, data=data)
        # Crear y guardar el nuevo empleado según el rol
        if rol_seleccionado == 'Administrador':
            nuevo = Administrador(
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                telefono=telefono,
                nacionalidad=nacionalidad,
                email=email,
                contrasena=contrasena,
                rol=rol_db
            )
        elif rol_seleccionado == 'Encargado':
            nuevo = Encargado(
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                telefono=telefono,
                nacionalidad=nacionalidad,
                email=email,
                contrasena=contrasena,
                rol=rol_db
            )
        else:  # pragma: no cover
            raise ValueError("Rol inválido recibido en agregar_empleado")
        db.session.add(nuevo)
        db.session.commit()
        flash('Registro exitoso', 'success')
        return render_template('agregar_empleado.html', roles=roles_permitidos)
    return render_template('agregar_empleado.html', roles=roles_permitidos)

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