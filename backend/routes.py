from flask import Blueprint, render_template, request, redirect, url_for

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
