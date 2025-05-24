from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models.propiedad import Propiedad
from sqlalchemy.sql.expression import func
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
    propiedades_random = Propiedad.query.filter_by(eliminado=False).order_by(func.random()).limit(6).all()
    return render_template('index.html', propiedades_random=propiedades_random)


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
@main.route('/propiedades/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_propiedad(id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.update_propiedad(id)

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

@main.route('/ver-propiedades')
@login_required
def ver_propiedades():
    propiedad_controller = PropiedadController()
    return propiedad_controller.list_propiedades(request, session)

@main.route('/propiedad/<int:id>')
@login_required
def detalle_propiedad(id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.get_propiedad(id)
   

@main.route('/recuperar-contraseña', methods=['GET', 'POST'])
def recuperar_contraseña():
    user_controller = UserController()
    return user_controller.recover_password(request)

@main.route('/cambiar-contraseña/<token>', methods=['GET', 'POST'])
def cambiar_contraseña(token):
    user_controller = UserController()
    return user_controller.change_password(request,token)

@main.route('/propiedad/eliminar/<int:id>', methods=['POST'])
def eliminar_propiedad(id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.eliminar_propiedad(id)

@main.route('/ver-administradores')
def ver_administradores():
    user_controller = UserController()
    return user_controller.ver_administradores(session)

@main.route('/ver-encargados')
def ver_encargados():
    user_controller = UserController()
    return user_controller.ver_encargados(session)

@main.route('/favoritos/agregar/<int:propiedad_id>', methods=['POST'])
@login_required
def agregar_favorito(propiedad_id):
    user_controller = UserController()
    return user_controller.agregar_favorito(session, propiedad_id)

@main.route('/favoritos/quitar/<int:propiedad_id>', methods=['POST'])
@login_required
def quitar_favorito(propiedad_id):
    user_controller = UserController()
    return user_controller.quitar_favorito(session, propiedad_id)

@main.route('/ver-favoritos')
@login_required
def ver_favoritos():
    user_controller = UserController()
    return user_controller.ver_favoritos(session)

@main.route('/propiedad/<int:id>/agregar-imagen', methods=['POST'])
@login_required
def agregar_imagen(id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.agregar_imagen(request, id)

@main.route('/imagen/eliminar/<int:imagen_id>', methods=['POST'])
@login_required
def eliminar_imagen(imagen_id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.eliminar_imagen(imagen_id)

@main.route('/encargado/eliminar/<int:id>', methods=['POST'])
def eliminar_encargado(id):
    user_controller = UserController()
    return user_controller.eliminar_encargado(session, id)

@main.route('/administrador/eliminar/<int:id>', methods=['POST'])
def eliminar_administrador(id):
    user_controller = UserController()
    return user_controller.eliminar_administrador(session, id)

@main.route('/encargado/<int:encargado_id>/propiedades/asignar')
def ver_propiedades_asignar(encargado_id):
    from architectural_patterns.controller.propiedad_controller import PropiedadController
    propiedad_controller = PropiedadController()
    return propiedad_controller.ver_propiedades_asignar(session, encargado_id)

@main.route('/encargado/<int:encargado_id>/propiedades/desasignar')
def ver_propiedades_desasignar(encargado_id):
    from architectural_patterns.controller.propiedad_controller import PropiedadController
    propiedad_controller = PropiedadController()
    return propiedad_controller.ver_propiedades_desasignar(session, encargado_id)

@main.route('/propiedad/<int:propiedad_id>/asignar/<int:encargado_id>', methods=['POST'])
def asignar_propiedad(propiedad_id, encargado_id):
    from architectural_patterns.controller.propiedad_controller import PropiedadController
    propiedad_controller = PropiedadController()
    return propiedad_controller.asignar_propiedad(session, propiedad_id, encargado_id)

@main.route('/propiedad/<int:propiedad_id>/desasignar', methods=['POST'])
def desasignar_propiedad(propiedad_id):
    from architectural_patterns.controller.propiedad_controller import PropiedadController
    propiedad_controller = PropiedadController()
    return propiedad_controller.desasignar_propiedad(session, propiedad_id)
