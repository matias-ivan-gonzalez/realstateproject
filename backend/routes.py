from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.user import Cliente
from database import db
from datetime import datetime
from architectural_patterns.service.user_service import UserService
from models.user import Administrador, Encargado, Usuario
from models.rol import Rol
from database import db
from architectural_patterns.service.propiedad_service import PropiedadService
from architectural_patterns.service.search_service import SearchService

# Crear un Blueprint para las rutas
main = Blueprint('main', __name__)

# Ruta principal
@main.route('/')
def index():
    return render_template('index.html')

# Ruta de login
@main.route('/login', methods=['GET', 'POST'])
def login():
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