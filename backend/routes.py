from functools import wraps
from models.propiedad import Propiedad
from sqlalchemy.sql.expression import func
from architectural_patterns.controller.user_controller import UserController
from architectural_patterns.controller.empleado_controller import EmpleadoController
from architectural_patterns.controller.propiedad_controller import PropiedadController
from architectural_patterns.controller.busqueda_controller import SearchController
import os
from models.calificacion import Calificacion
def estadisticas_propiedad(propiedad_id):
    from models.propiedad import Propiedad
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    # Parámetros de mes y año
    mes = request.args.get('mes', datetime.now().month, type=int)
    anio = request.args.get('anio', datetime.now().year, type=int)
    reservas = Reserva.query.filter_by(propiedad_id=propiedad_id).all()
    # Filtrar reservas del mes/año
    reservas_mes = [r for r in reservas if r.fecha_inicio.month == mes and r.fecha_inicio.year == anio]
    reservas_concretadas = len([r for r in reservas_mes if r.estado == 'concretada'])
    reservas_canceladas = len([r for r in reservas_mes if r.estado == 'cancelada'])
    total_noches = sum((r.fecha_fin - r.fecha_inicio).days for r in reservas_mes if r.estado == 'concretada')
    promedio_dias_reserva = round(total_noches / reservas_concretadas, 2) if reservas_concretadas else 0
    # Porcentaje de ocupación
    dias_mes = (date(anio, mes % 12 + 1, 1) - date(anio, mes, 1)).days if mes < 12 else 31
    porcentaje_ocupacion = round((total_noches / dias_mes) * 100, 2) if dias_mes else 0
    # Ingresos estimados
    ingresos_estimados = round(total_noches * propiedad.precio, 2)
def estadisticas_propiedad(propiedad_id):
    from models.propiedad import Propiedad
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    # Parámetros de mes y año
    mes = request.args.get('mes', datetime.now().month, type=int)
    anio = request.args.get('anio', datetime.now().year, type=int)
    reservas = Reserva.query.filter_by(propiedad_id=propiedad_id).all()
    # Filtrar reservas del mes/año
    reservas_mes = [r for r in reservas if r.fecha_inicio.month == mes and r.fecha_inicio.year == anio]
    reservas_concretadas = len([r for r in reservas_mes if r.estado == 'concretada'])
    reservas_canceladas = len([r for r in reservas_mes if r.estado == 'cancelada'])
    total_noches = sum((r.fecha_fin - r.fecha_inicio).days for r in reservas_mes if r.estado == 'concretada')
    promedio_dias_reserva = round(total_noches / reservas_concretadas, 2) if reservas_concretadas else 0
    # Porcentaje de ocupación
    dias_mes = (date(anio, mes % 12 + 1, 1) - date(anio, mes, 1)).days if mes < 12 else 31
    porcentaje_ocupacion = round((total_noches / dias_mes) * 100, 2) if dias_mes else 0
    # Ingresos estimados
    ingresos_estimados = round(total_noches * propiedad.precio, 2)
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date
from models.reserva import Reserva

# Crear un Blueprint para las rutas
main = Blueprint('main', __name__)

@main.route('/propiedad/<int:propiedad_id>/estadisticas')
def estadisticas_propiedad(propiedad_id):
    from models.propiedad import Propiedad
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    # Parámetros de mes y año
    mes = request.args.get('mes', datetime.now().month, type=int)
    anio = request.args.get('anio', datetime.now().year, type=int)
    reservas = Reserva.query.filter_by(propiedad_id=propiedad_id).all()
    # Filtrar reservas del mes/año
    reservas_mes = [r for r in reservas if r.fecha_inicio.month == mes and r.fecha_inicio.year == anio]
    reservas_concretadas = len([r for r in reservas_mes if r.estado == 'concretada'])
    reservas_canceladas = len([r for r in reservas_mes if r.estado == 'cancelada'])
    total_noches = sum((r.fecha_fin - r.fecha_inicio).days for r in reservas_mes if r.estado == 'concretada')
    promedio_dias_reserva = round(total_noches / reservas_concretadas, 2) if reservas_concretadas else 0
    # Porcentaje de ocupación
    dias_mes = (date(anio, mes % 12 + 1, 1) - date(anio, mes, 1)).days if mes < 12 else 31
    porcentaje_ocupacion = round((total_noches / dias_mes) * 100, 2) if dias_mes else 0
    # Ingresos estimados
    ingresos_estimados = round(total_noches * propiedad.precio, 2)
    reservas_anio = len([r for r in reservas if r.fecha_inicio.year == anio and r.estado == 'concretada'])
    anio_actual = datetime.now().year
    return render_template('estadisticas_propiedad.html', propiedad=propiedad, mes=mes, anio=anio, anio_actual=anio_actual,
        reservas_concretadas=reservas_concretadas, reservas_canceladas=reservas_canceladas, promedio_dias_reserva=promedio_dias_reserva,
        total_noches=total_noches, porcentaje_ocupacion=porcentaje_ocupacion, ingresos_estimados=ingresos_estimados, reservas_anio=reservas_anio)
    reservas_anio = len([r for r in reservas if r.fecha_inicio.year == anio and r.estado == 'concretada'])
    anio_actual = datetime.now().year
    return render_template('estadisticas_propiedad.html', propiedad=propiedad, mes=mes, anio=anio, anio_actual=anio_actual,
        reservas_concretadas=reservas_concretadas, reservas_canceladas=reservas_canceladas, promedio_dias_reserva=promedio_dias_reserva,
        total_noches=total_noches, porcentaje_ocupacion=porcentaje_ocupacion, ingresos_estimados=ingresos_estimados, reservas_anio=reservas_anio)


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

@main.route('/favoritos/quitar/<int:propiedad_id>', methods=['GET', 'POST'])
@login_required
def quitar_favorito(propiedad_id):
    if request.method == 'GET':
        return redirect(url_for('main.ver_favoritos'))
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

@main.route('/administrador/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_administrador(id):
    user_controller = UserController()
    return user_controller.eliminar_administrador(session, id)

@main.route('/encargado/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_encargado(id):
    user_controller = UserController()
    return user_controller.eliminar_encargado(session, id)

@main.route('/encargado/<int:encargado_id>/asignar-propiedades')
@login_required
def ver_propiedades_asignar(encargado_id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.ver_propiedades_asignar(session, encargado_id)

@main.route('/encargado/<int:encargado_id>/desasignar-propiedades')
@login_required
def ver_propiedades_desasignar(encargado_id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.ver_propiedades_desasignar(session, encargado_id)

@main.route('/propiedad/desasignar/<int:propiedad_id>', methods=['POST'])
@login_required
def desasignar_propiedad(propiedad_id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.desasignar_propiedad(session, propiedad_id)

@main.route('/propiedad/asignar/<int:propiedad_id>/<int:encargado_id>', methods=['POST'])
@login_required
def asignar_propiedad(propiedad_id, encargado_id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.asignar_propiedad(session, propiedad_id, encargado_id)

def get_archivos_carpeta(carpeta):
    """Obtiene la lista de archivos de una carpeta ordenados alfabéticamente."""
    ruta_carpeta = os.path.join(os.getcwd(), carpeta.lstrip('/').replace('/', os.sep))
    if os.path.exists(ruta_carpeta):
        archivos = [f for f in os.listdir(ruta_carpeta) if os.path.isfile(os.path.join(ruta_carpeta, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        return sorted(archivos)
    return []

# Registrar la función en el contexto de Jinja2
main.add_app_template_global(get_archivos_carpeta)
@main.route('/cambiar-contrasena', methods=['POST'])
@login_required
def cambiar_contrasena():
    from architectural_patterns.controller.user_controller import UserController
    user_controller = UserController()
    return user_controller.cambiar_contrasena_perfil(request, session)

@main.route('/ver-reservas')
@login_required
def ver_reservas():
    user_controller = UserController()
    return user_controller.ver_reservas(session)

@main.route('/propiedad/ocupar/<int:propiedad_id>', methods=['POST'])
@login_required
def ocupar_propiedad(propiedad_id):
    propiedad_controller = PropiedadController()
    return propiedad_controller.ocupar_propiedad(request, session, propiedad_id)

# Ruta para calificar propiedad
@main.route('/calificar/<int:reserva_id>', methods=['GET', 'POST'])
@login_required
def calificar_propiedad(reserva_id):
    user_controller = UserController()
    if request.method == 'POST':
        return user_controller.procesar_calificacion(session, reserva_id, request.form)
    else:
        return user_controller.mostrar_formulario_calificacion(session, reserva_id)

@main.route('/editar-calificacion/<int:calificacion_id>', methods=['GET', 'POST'])
@login_required
def editar_calificacion(calificacion_id):
    user_controller = UserController()
    if request.method == 'POST':
        return user_controller.procesar_edicion_calificacion(session, calificacion_id, request.form)
    else:
        return user_controller.mostrar_formulario_editar_calificacion(session, calificacion_id)

@main.route('/borrar-calificacion/<int:calificacion_id>', methods=['POST'])
@login_required
def borrar_calificacion(calificacion_id):
    user_controller = UserController()
    return user_controller.borrar_calificacion(session, calificacion_id)

@main.route('/propiedad/<int:propiedad_id>/reservas')
@login_required
def ver_reservas_propiedad(propiedad_id):
    from models.propiedad import Propiedad
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    reservas = propiedad.reservas
    return render_template('reservas_propiedad.html', reservas=reservas, propiedad=propiedad)

from flask import request
@main.route('/chat')
def chat():
    from flask import session
    from models.conversacion import Conversacion
    reserva_id = request.args.get('reserva_id')
    tipo = request.args.get('tipo')
    conversacion_id = request.args.get('conversacion_id')
    conversacion = None
    if conversacion_id:
        conversacion = Conversacion.query.get(conversacion_id)
    elif session.get('rol') == 'cliente':
        conversacion = Conversacion.query.filter_by(reserva_id=reserva_id, tipo=tipo, cliente_id=session.get('user_id')).first()
    estado_chat = conversacion.estado if conversacion else 'abierta'
    return render_template('chat.html', session=session, reserva_id=reserva_id, tipo=tipo, estado_chat=estado_chat)

@main.route('/ver-chats')
@login_required
def ver_chats():
    if session.get('rol') not in ['administrador', 'superusuario']:
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    from models.conversacion import Conversacion
    from models.user import Cliente
    from models.reserva import Reserva
    from models.propiedad import Propiedad

    # Obtener todas las conversaciones abiertas, agrupadas por tipo
    chats_futuro = Conversacion.query.filter_by(tipo='futuro', estado='abierta').all()
    chats_curso = Conversacion.query.filter_by(tipo='curso', estado='abierta').all()
    chats_futuro_cerradas = Conversacion.query.filter_by(tipo='futuro', estado='cerrada').all()
    chats_curso_cerradas = Conversacion.query.filter_by(tipo='curso', estado='cerrada').all()

    def serializar_chat(chat):
        cliente = Cliente.query.get(chat.cliente_id)
        reserva = Reserva.query.get(chat.reserva_id)
        propiedad = Propiedad.query.get(reserva.propiedad_id) if reserva else None
        return {
            'id': chat.id,
            'cliente_id': chat.cliente_id,
            'cliente_nombre': f"{cliente.nombre} {cliente.apellido}" if cliente else f"Cliente {chat.cliente_id}",
            'reserva_id': chat.reserva_id,
            'casa_nombre': propiedad.nombre if propiedad else "Propiedad desconocida",
            'fecha_inicio': reserva.fecha_inicio.strftime('%Y-%m-%d') if reserva else "Fecha desconocida",
            'fecha_fin': reserva.fecha_fin.strftime('%Y-%m-%d') if reserva else "Fecha desconocida"
        }

    chats_futuro = [serializar_chat(c) for c in chats_futuro]
    chats_curso = [serializar_chat(c) for c in chats_curso]
    chats_futuro_cerradas = [serializar_chat(c) for c in chats_futuro_cerradas]
    chats_curso_cerradas = [serializar_chat(c) for c in chats_curso_cerradas]
    return render_template('ver_chats.html', chats_futuro=chats_futuro, chats_curso=chats_curso, chats_futuro_cerradas=chats_futuro_cerradas, chats_curso_cerradas=chats_curso_cerradas)


from architectural_patterns.controller.user_controller import UserController
user_controller = UserController()

@main.route('/reservas/futuras')
def reservas_futuras():
    reservas = user_controller.obtener_reservas_futuras(session)
    current_date = datetime.now().date()
    return render_template('reservas_futuras.html', reservas=reservas, current_date=current_date)

@main.route('/reservas/concluidas')
def reservas_concluidas():
    reservas = user_controller.obtener_reservas_concluidas(session)
    current_date = datetime.now().date()
    return render_template('reservas_concluidas.html', reservas=reservas, current_date=current_date)

@main.route('/reservas/pendientes')
def calificaciones_pendientes():
    reservas = user_controller.obtener_calificaciones_pendientes(session)
    current_date = datetime.now().date()
    return render_template('calificaciones_pendientes.html', reservas=reservas, current_date=current_date)

@main.route('/reservas/editables')
def calificaciones_editables():
    reservas = user_controller.obtener_calificaciones_editables(session)
    current_date = datetime.now().date()
    return render_template('calificaciones_editables.html', reservas=reservas, current_date=current_date)

@main.route('/reservas/activas')
def reservas_activas():
    user_controller = UserController()
    reservas = user_controller.obtener_reservas_activas(session)
    current_date = datetime.now().date()
    return render_template('reservas_activas.html', reservas=reservas, current_date=current_date)