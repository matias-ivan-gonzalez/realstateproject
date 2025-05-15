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

@main.route('/search', methods=['GET'])
def search():
    from models.Propiedad import Propiedad
    ubicacion = request.args.get('ubicacion', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')

    # Filtrar propiedades por ubicación (búsqueda simple)
    propiedades = []
    if ubicacion:
        propiedades = Propiedad.query.filter(Propiedad.ubicacion.ilike(f"%{ubicacion}%")).all()
    else:
        propiedades = Propiedad.query.all()

    # Aquí podrías agregar lógica para filtrar por fechas si tienes reservas
    # Por ahora, solo se filtra por ubicación

    return render_template('search_results.html', propiedades=propiedades, ubicacion=ubicacion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
