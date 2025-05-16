from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.user import Cliente
from database import db
from datetime import datetime
from architectural_patterns.service.user_service import UserService

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