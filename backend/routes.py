from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.user import Administrador, Encargado, Usuario
from models.rol import Rol
from database import db

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
        # Aquí podrías capturar los datos del formulario si es necesario
        # nombre = request.form.get('nombre')
        # Procesar datos o guardar en la base de datos

        return redirect(url_for('main.login'))  # Redirige al login después del registro

    return render_template('register.html')

# Ruta para mostrar el formulario de nueva propiedad
@main.route('/propiedades/nueva', methods=['GET', 'POST'])
def nueva_propiedad():
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
        db.session.add(nuevo)
        db.session.commit()
        flash('Registro exitoso', 'success')
        return render_template('agregar_empleado.html', roles=roles_permitidos)
    return render_template('agregar_empleado.html', roles=roles_permitidos)