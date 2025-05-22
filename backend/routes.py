from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from architectural_patterns.controller.user_controller import UserController
from architectural_patterns.controller.empleado_controller import EmpleadoController
from architectural_patterns.controller.propiedad_controller import PropiedadController
from architectural_patterns.controller.busqueda_controller import SearchController





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


@main.route('/login', methods=['GET', 'POST'])
def login():
    user_controller = UserController()
    return user_controller.login(request, session)

# Ruta de registro
@main.route('/register', methods=['GET', 'POST'])
def registrarse():
    user_controller = UserController()
    return user_controller.register(request)

@main.route('/search', methods=['GET'])
def search_properties():
    search_controller = SearchController()
    return search_controller.search_properties(request)
           


# Ruta para mostrar el formulario de nueva propiedad
@main.route('/propiedades/nueva', methods=['GET', 'POST'])
def nueva_propiedad():
    propiedad_controller = PropiedadController()
    return propiedad_controller.add_propiedad(request)
    

# Ruta para mostrar el formulario de modificar propiedad
@main.route('/propiedades/modificar', methods=['GET', 'POST'])
def modificar_propiedad():
    # Diccionario de ejemplo con datos de una propiedad
    propiedad_controller = PropiedadController()
    return propiedad_controller.update_propiedad()

# Ruta para agregar un nuevo empleado (administrador o encargado)
@main.route('/empleados/nuevo', methods=['GET', 'POST'])
def agregar_empleado():
    empleado_controller = EmpleadoController()
    return empleado_controller.add_empleado(session, request)

@main.route('/logout', methods=['POST'])
def logout():
    user_controller = UserController()
    return user_controller.logout(session)
    

@main.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    user_controller = UserController()
    return user_controller.profile(request, session)


@main.route('/perfil/eliminar', methods=['POST'])
@login_required
def eliminar_cuenta():
    user_controller = UserController()
    return user_controller.delete_account(session)
