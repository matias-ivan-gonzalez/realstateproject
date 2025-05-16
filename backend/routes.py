from flask import Blueprint, render_template, request, redirect, url_for, flash
from architectural_patterns.service.propiedad_service import PropiedadService

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
            return redirect(url_for('main.index'))
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