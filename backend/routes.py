


from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models.propiedad import Propiedad
from sqlalchemy.sql.expression import func
from architectural_patterns.controller.user_controller import UserController
from architectural_patterns.controller.empleado_controller import EmpleadoController
from architectural_patterns.controller.propiedad_controller import PropiedadController
from architectural_patterns.controller.busqueda_controller import SearchController
import os
from models.calificacion import Calificacion
from models.reserva import Reserva
from models.user import Cliente
from database import db
from config import MERCADOPAGO_ACCESS_TOKEN
import mercadopago
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date, timedelta
from models.reserva import Reserva
from models.pago import Pago

# Crear un Blueprint para las rutas
main = Blueprint('main', __name__)

@main.route('/propiedad/<int:propiedad_id>/estadisticas')
def estadisticas_propiedad(propiedad_id):
    if 'rol' not in session or session['rol'] not in ['administrador', 'superusuario']:
        flash('Solo los administradores pueden acceder a las estadísticas de propiedad.', 'danger')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    from architectural_patterns.controller.propiedad_controller import PropiedadController
    from datetime import datetime
    mes = request.args.get('mes', datetime.now().month, type=int)
    anio = request.args.get('anio', datetime.now().year, type=int)
    controller = PropiedadController()
    propiedad, estadisticas = controller.get_estadisticas_propiedad(propiedad_id, mes, anio)
    anio_actual = datetime.now().year
    return render_template('estadisticas_propiedad.html',
        propiedad=propiedad, mes=mes, anio=anio, anio_actual=anio_actual,
        **estadisticas
    )
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
    from architectural_patterns.controller.reserva_controller import ReservaController
    pago_status = request.args.get('pago')
    if pago_status == 'success':
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        huespedes = request.args.get('huespedes')
        if fecha_inicio and fecha_fin and huespedes:
            ReservaController().crear_reserva_checkout(session.get('user_id'), id, fecha_inicio, fecha_fin, int(huespedes))
        return redirect(url_for('main.detalle_propiedad', id=id))
    elif pago_status == 'failure':
        session['show_reserva_fallida_flash'] = True
        return redirect(url_for('main.detalle_propiedad', id=id))
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

@main.route('/propiedad/<int:propiedad_id>/reservar', methods=['POST'])
@login_required
def reservar_propiedad(propiedad_id):
    from architectural_patterns.controller.reserva_controller import ReservaController
    return ReservaController().reservar_propiedad_post(request, session, propiedad_id)

@main.route('/crear_preferencia_checkout', methods=['POST'])
@login_required
def crear_preferencia_checkout():
    from architectural_patterns.controller.reserva_controller import ReservaController
    return ReservaController().crear_preferencia_checkout(request, session)

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
    from models.mensaje_chat import MensajeChat
    reserva_id = request.args.get('reserva_id')
    tipo = request.args.get('tipo')
    conversacion_id = request.args.get('conversacion_id')
    fusion = request.args.get('fusion') == '1'
    conversacion_ids = request.args.get('conversacion_ids')
    mensajes = []
    estado_chat = 'abierta'
    chat_cerrado = False
    conversacion = None

    if fusion and conversacion_ids:
        # Fusionar mensajes de varias conversaciones
        ids = [int(cid) for cid in conversacion_ids.split(',') if cid.isdigit()]
        conversaciones = Conversacion.query.filter(Conversacion.id.in_(ids)).all()
        if conversaciones:
            reserva_id = conversaciones[0].reserva_id
            tipo = conversaciones[0].tipo
            # Obtener todos los mensajes de todas las conversaciones
            for conv in conversaciones:
                mensajes += MensajeChat.query.filter_by(conversacion_id=conv.id).all()
            mensajes.sort(key=lambda m: m.timestamp)
            mensajes = [m.to_dict() for m in mensajes]
            # Si todas las conversaciones están cerradas, marcar como cerrado
            if all(conv.estado == 'cerrada' for conv in conversaciones):
                estado_chat = 'cerrada'
                chat_cerrado = True
            else:
                estado_chat = 'abierta'
        else:
            mensajes = []
    else:
        if conversacion_id:
            conversacion = Conversacion.query.get(conversacion_id)
            if conversacion:
                reserva_id = conversacion.reserva_id
                tipo = conversacion.tipo
                estado_chat = conversacion.estado
                mensajes = [m.to_dict() for m in MensajeChat.query.filter_by(conversacion_id=conversacion.id).order_by(MensajeChat.timestamp).all()]
                if conversacion.estado == 'cerrada':
                    chat_cerrado = True
        elif session.get('rol') == 'cliente':
            conversacion = Conversacion.query.filter_by(reserva_id=reserva_id, tipo=tipo, cliente_id=session.get('user_id')).first()
            if conversacion:
                estado_chat = conversacion.estado
                mensajes = [m.to_dict() for m in MensajeChat.query.filter_by(conversacion_id=conversacion.id).order_by(MensajeChat.timestamp).all()]
                if conversacion.estado == 'cerrada':
                    chat_cerrado = True

    return render_template('chat.html', session=session, reserva_id=reserva_id, tipo=tipo, estado_chat=estado_chat, mensajes=mensajes, chat_cerrado=chat_cerrado)

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


    # Solo mostrar a los administradores/superusuarios los chats donde la propiedad NO tiene encargado asignado

    def filtrar_chats_para_admin(chats, tipo):
        filtrados = []
        for chat in chats:
            reserva = Reserva.query.get(chat.reserva_id)
            if not reserva:
                continue
            propiedad = Propiedad.query.get(reserva.propiedad_id)
            if tipo == 'futuro':
                # Para reservas a futuro, siempre son los administradores
                if session.get('rol') == 'superusuario':
                    filtrados.append(chat)
                elif session.get('rol') == 'administrador':
                    if session.get('user_id') in [a.id for a in propiedad.administradores]:
                        filtrados.append(chat)
            else:
                # Para reservas en curso, solo si NO hay encargado asignado
                if propiedad and not propiedad.encargado_id:
                    if session.get('rol') == 'superusuario':
                        filtrados.append(chat)
                    elif session.get('rol') == 'administrador':
                        if session.get('user_id') in [a.id for a in propiedad.administradores]:
                            filtrados.append(chat)
        return filtrados

    chats_futuro = filtrar_chats_para_admin(Conversacion.query.filter_by(tipo='futuro', estado='abierta').all(), 'futuro')
    chats_curso = filtrar_chats_para_admin(Conversacion.query.filter_by(tipo='curso', estado='abierta').all(), 'curso')

    chats_futuro_cerradas = filtrar_chats_para_admin(Conversacion.query.filter_by(tipo='futuro', estado='cerrada').all(), 'futuro')
    chats_curso_cerradas = filtrar_chats_para_admin(Conversacion.query.filter_by(tipo='curso', estado='cerrada').all(), 'curso')
    todas_cerradas = chats_futuro_cerradas + chats_curso_cerradas
    # Fusionar conversaciones cerradas por reserva_id
    from models.mensaje_chat import MensajeChat
    chats_cerradas_dict = {}
    for chat in todas_cerradas:
        if chat.reserva_id not in chats_cerradas_dict:
            chats_cerradas_dict[chat.reserva_id] = []
        chats_cerradas_dict[chat.reserva_id].append(chat)
    chats_cerradas_fusionadas = []
    for reserva_id, chats in chats_cerradas_dict.items():
        # Fusionar mensajes de todas las conversaciones cerradas de la reserva
        mensajes = []
        for chat in chats:
            mensajes += MensajeChat.query.filter_by(conversacion_id=chat.id).all()
        mensajes.sort(key=lambda m: (getattr(m, 'timestamp', None) or getattr(m, 'fecha_envio', None) or m.id))
        chat_base = chats[0]
        cliente = Cliente.query.get(chat_base.cliente_id)
        reserva = Reserva.query.get(reserva_id)
        propiedad = Propiedad.query.get(reserva.propiedad_id) if reserva else None
        chats_cerradas_fusionadas.append({
            'id': max([c.id for c in chats]),
            'cliente_id': chat_base.cliente_id,
            'cliente_nombre': f"{cliente.nombre} {cliente.apellido}" if cliente else f"Cliente {chat_base.cliente_id}",
            'reserva_id': reserva_id,
            'casa_nombre': propiedad.nombre if propiedad else "Propiedad desconocida",
            'fecha_inicio': reserva.fecha_inicio.strftime('%Y-%m-%d') if reserva else "Fecha desconocida",
            'fecha_fin': reserva.fecha_fin.strftime('%Y-%m-%d') if reserva else "Fecha desconocida",
            'mensajes': [
                {
                    'id': m.id,
                    'conversacion_id': m.conversacion_id,
                    'user': m.user,
                    'rol': m.rol,
                    'msg': m.msg,
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S') if getattr(m, 'timestamp', None) else None
                } for m in mensajes
            ],
            'conversacion_ids': [c.id for c in chats],
            'tipo': ','.join(sorted(set([c.tipo for c in chats])))
        })

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
    # chats_cerradas_fusionadas ya está serializado y contiene los mensajes fusionados
    return render_template('ver_chats.html', chats_futuro=chats_futuro, chats_curso=chats_curso, chats_cerradas=chats_cerradas_fusionadas)


from architectural_patterns.controller.user_controller import UserController
user_controller = UserController()

@main.route('/reservas/futuras')
def reservas_futuras():
    if session.pop('show_extension_flash', None):
        flash('Reserva extendida, se programa el cobro en la tarjeta registrada en la próxima liquidación diaria', 'success')
    reservas = user_controller.obtener_reservas_futuras(session)
    current_date = datetime.now().date()
    # Armar fechas ocupadas y reservadas para todas las propiedades de las reservas
    from models.propiedad import Propiedad
    fechas_ocupadas = []
    fechas_reservadas = []
    for r in reservas:
        propiedad = Propiedad.query.filter_by(nombre=r['propiedad']).first()
        if propiedad:
            for ocup in getattr(propiedad, 'ocupaciones', []):
                fechas_ocupadas.append({
                    'inicio': ocup.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': ocup.fecha_fin.strftime('%Y-%m-%d')
                })
            for res in getattr(propiedad, 'reservas', []):
                fechas_reservadas.append({
                    'inicio': res.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': res.fecha_fin.strftime('%Y-%m-%d')
                })
    return render_template('reservas_futuras.html', reservas=reservas, current_date=current_date, fechas_ocupadas=fechas_ocupadas, fechas_reservadas=fechas_reservadas)

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
    if session.pop('show_extension_flash', None):
        flash('Reserva extendida, se programa el cobro en la tarjeta registrada en la próxima liquidación diaria', 'success')
    user_controller = UserController()
    reservas = user_controller.obtener_reservas_activas(session)
    current_date = datetime.now().date()
    from models.propiedad import Propiedad
    fechas_ocupadas = []
    fechas_reservadas = []
    for r in reservas:
        propiedad = Propiedad.query.filter_by(nombre=r['propiedad']).first()
        if propiedad:
            for ocup in getattr(propiedad, 'ocupaciones', []):
                fechas_ocupadas.append({
                    'inicio': ocup.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': ocup.fecha_fin.strftime('%Y-%m-%d')
                })
            for res in getattr(propiedad, 'reservas', []):
                fechas_reservadas.append({
                    'inicio': res.fecha_inicio.strftime('%Y-%m-%d'),
                    'fin': res.fecha_fin.strftime('%Y-%m-%d')
                })
    return render_template('reservas_activas.html', reservas=reservas, current_date=current_date, fechas_ocupadas=fechas_ocupadas, fechas_reservadas=fechas_reservadas)


@main.route('/ver-mis-chats-encargado')
def ver_mis_chats_encargado():
    if session.get('rol') != 'encargado':
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    from models.conversacion import Conversacion
    from models.user import Cliente
    from models.reserva import Reserva
    from models.propiedad import Propiedad


    # Obtener las conversaciones del encargado a través de sus propiedades
    encargado_id = session.get('user_id')
    propiedades_encargado = Propiedad.query.filter_by(encargado_id=encargado_id).all()
    propiedad_ids = [p.id for p in propiedades_encargado]
    reservas_encargado = Reserva.query.filter(Reserva.propiedad_id.in_(propiedad_ids)).all() if propiedad_ids else []
    reserva_ids = [r.id for r in reservas_encargado]
    # Solo mostrar conversaciones en curso (tipo='curso')
    chats = Conversacion.query.filter(
        Conversacion.reserva_id.in_(reserva_ids),
        Conversacion.tipo == 'curso'
    ).all() if reserva_ids else []

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

    chats_serializados = [serializar_chat(c) for c in chats]
    return render_template('ver_mis_chats_encargado.html', chats=chats_serializados)

@main.route('/extender_reserva', methods=['POST'])
@login_required
def extender_reserva():
    from flask import request, jsonify
    from datetime import datetime, timedelta
    from architectural_patterns.controller.reserva_controller import ReservaController
    data = request.get_json()
    reserva_id = data.get('reserva_id')
    nueva_fecha_fin = data.get('nueva_fecha_fin')
    if not reserva_id or not nueva_fecha_fin:
        return jsonify({'error': 'Datos incompletos'}), 400
    try:
        nueva_fecha_fin_dt = datetime.strptime(nueva_fecha_fin, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Fecha inválida'}), 400
    controller = ReservaController()
    return controller.extender_reserva(session, reserva_id, nueva_fecha_fin_dt)

@main.route('/extender_reserva_success')
@login_required
def extender_reserva_success():
    from flask import request, redirect, url_for, flash
    reserva_id = request.args.get('reserva_id')
    nueva_fecha_fin = request.args.get('nueva_fecha_fin')
    if not reserva_id or not nueva_fecha_fin:
        flash('Extensión de reserva fallida (datos incompletos)', 'danger')
        return redirect(url_for('main.ver_reservas'))
    from models.reserva import Reserva
    from database import db
    from datetime import datetime
    reserva = Reserva.query.get(reserva_id)
    if not reserva:
        flash('Reserva no encontrada', 'danger')
        return redirect(url_for('main.ver_reservas'))
    try:
        nueva_fecha_fin_dt = datetime.strptime(nueva_fecha_fin, '%Y-%m-%d').date()
        if nueva_fecha_fin_dt > reserva.fecha_fin:
            reserva.fecha_fin = nueva_fecha_fin_dt
            db.session.commit()
            flash('Reserva extendida', 'success')
        else:
            flash('La nueva fecha de salida debe ser posterior a la actual', 'danger')
    except Exception:
        flash('Error al procesar la extensión', 'danger')
    return redirect(url_for('main.ver_reservas'))

@main.route('/clientes-calificables')
@login_required
def clientes_calificables():
    from architectural_patterns.service.user_service import UserService
    if 'user_id' not in session or session.get('rol') != 'encargado':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('main.index'))
    user_service = UserService()
    reservas = user_service.get_reservas_calificables_por_encargado(session['user_id'])
    return render_template('encargado/clientes_calificables.html', reservas=reservas)

@main.route('/calificar-cliente/<int:reserva_id>', methods=['GET', 'POST'])
@login_required
def calificar_cliente(reserva_id):
    from models.reserva import Reserva
    from models.calificacion_cliente import CalificacionCliente
    from models.user import Encargado
    if 'user_id' not in session or session.get('rol') != 'encargado':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('main.index'))
    reserva = Reserva.query.get_or_404(reserva_id)
    if request.method == 'POST':
        opinion = request.form.get('opinion', '').strip()
        if not opinion:
            flash('Debes ingresar una opinión.', 'warning')
            return render_template('encargado/calificar_cliente.html', reserva=reserva)
        ya_calificada = CalificacionCliente.query.filter_by(reserva_id=reserva.id).first()
        if ya_calificada:
            flash('Ya has calificado a este cliente para esta reserva.', 'info')
            return redirect(url_for('main.clientes_calificables'))
        calif = CalificacionCliente(
            reserva_id=reserva.id,
            encargado_id=session['user_id'],
            cliente_id=reserva.cliente_id,
            opinion=opinion
        )
        from database import db
        db.session.add(calif)
        db.session.commit()
        flash('Calificación registrada correctamente.', 'success')
        return redirect(url_for('main.clientes_calificables'))
    return render_template('encargado/calificar_cliente.html', reserva=reserva)

@main.route('/calificaciones-editables-clientes')
@login_required
def calificaciones_editables_clientes():
    if 'user_id' not in session or session.get('rol') != 'encargado':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('main.index'))
    from architectural_patterns.service.user_service import UserService
    user_service = UserService()
    reservas = user_service.get_calificaciones_editables_clientes_por_encargado(session['user_id'])
    return render_template('calificaciones_editables_encargado.html', reservas=reservas)

@main.route('/editar-calificacion-cliente/<int:calificacion_id>', methods=['GET', 'POST'])
@login_required
def editar_calificacion_cliente(calificacion_id):
    from models.calificacion_cliente import CalificacionCliente
    from database import db
    from datetime import date
    calificacion = CalificacionCliente.query.get_or_404(calificacion_id)
    reserva = calificacion.reserva
    hoy = date.today()
    dias_diferencia = (hoy - reserva.fecha_fin).days
    if dias_diferencia > 30:
        flash('Solo puedes editar la calificación hasta 30 días después de la estadía.', 'warning')
        return redirect(url_for('main.calificaciones_editables_clientes'))
    if request.method == 'POST':
        opinion = request.form.get('opinion', '').strip()
        if not opinion:
            flash('Debes ingresar una opinión.', 'warning')
            return render_template('encargado/calificar_cliente.html', reserva=reserva, calificacion=calificacion, editar=True)
        calificacion.opinion = opinion
        db.session.commit()
        flash('Calificación modificada con éxito', 'success')
        return redirect(url_for('main.calificaciones_editables_clientes'))
    return render_template('encargado/calificar_cliente.html', reserva=reserva, calificacion=calificacion, editar=True)

@main.route('/eliminar-calificacion-cliente/<int:calificacion_id>', methods=['POST'])
@login_required
def eliminar_calificacion_cliente(calificacion_id):
    from models.calificacion_cliente import CalificacionCliente
    from database import db
    from datetime import date
    calificacion = CalificacionCliente.query.get_or_404(calificacion_id)
    reserva = calificacion.reserva
    hoy = date.today()
    dias_diferencia = (hoy - reserva.fecha_fin).days
    if dias_diferencia > 30:
        flash('Solo puedes eliminar la calificación hasta 30 días después de la estadía.', 'warning')
        return redirect(url_for('main.calificaciones_editables_clientes'))
    db.session.delete(calificacion)
    db.session.commit()
    flash('Calificación eliminada exitosamente.', 'success')
    return redirect(url_for('main.calificaciones_editables_clientes'))

@main.route('/propiedades/sin-encargado')
@login_required
def propiedades_sin_encargado():
    if session.get('rol') not in ['administrador', 'superusuario']:
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    from models.propiedad import Propiedad
    from architectural_patterns.repository.empleado_repository import EmpleadoRepository
    propiedades = Propiedad.query.filter_by(encargado_id=None, eliminado=False).all()
    encargados = EmpleadoRepository().get_encargados()
    return render_template('propiedades_sin_encargado.html', propiedades=propiedades, encargados=encargados)

@main.route('/propiedad/<int:propiedad_id>/asignar-encargado', methods=['POST'])
@login_required
def asignar_encargado_a_propiedad(propiedad_id):
    if session.get('rol') not in ['administrador', 'superusuario']:
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('main.index'))
    encargado_id = request.form.get('encargado_id')
    if not encargado_id:
        flash('Debes seleccionar un encargado.', 'warning')
        return redirect(url_for('main.propiedades_sin_encargado'))
    from models.propiedad import Propiedad
    from models.reserva import Reserva
    from database import db
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    # Validar si hay reservas en curso
    reservas_curso = Reserva.query.filter_by(propiedad_id=propiedad.id, estado='curso').all()
    if reservas_curso:
        flash('No se puede asignar la propiedad porque tiene una reserva en curso.', 'warning')
        return redirect(url_for('main.propiedades_sin_encargado'))
    propiedad.encargado_id = int(encargado_id)
    db.session.commit()
    flash('Encargado asignado correctamente.', 'success')
    return redirect(url_for('main.propiedades_sin_encargado'))

@main.route('/propiedades/asignadas')
@login_required
def propiedades_asignadas():
    if session.get('rol') not in ['administrador', 'superusuario']:
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    from models.propiedad import Propiedad
    from models.user import Encargado
    propiedades = Propiedad.query.filter(Propiedad.encargado_id.isnot(None), Propiedad.eliminado == False).all()
    return render_template('propiedades_asignadas.html', propiedades=propiedades)

@main.route('/propiedad/<int:propiedad_id>/desasignar-encargado', methods=['POST'])
@login_required
def desasignar_encargado_de_propiedad(propiedad_id):
    if session.get('rol') not in ['administrador', 'superusuario']:
        flash('No tienes permiso para realizar esta acción.', 'danger')
        return redirect(url_for('main.index'))
    from models.propiedad import Propiedad
    from models.reserva import Reserva
    from database import db
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    # Validar si hay reservas en curso
    reservas_curso = Reserva.query.filter_by(propiedad_id=propiedad.id, estado='curso').all()
    if reservas_curso:
        flash('No se puede desasignar el encargado porque hay una estadía en curso en esta propiedad.', 'warning')
        return redirect(url_for('main.propiedades_asignadas'))
    propiedad.encargado_id = None
    db.session.commit()
    flash('Encargado desasignado correctamente.', 'success')
    return redirect(url_for('main.propiedades_asignadas'))

@main.route('/reserva/eliminar/<int:reserva_id>', methods=['POST'])
def eliminar_reserva(reserva_id):
    from models.reserva import Reserva
    from flask import redirect, url_for, flash
    from datetime import datetime, timedelta
    reserva = Reserva.query.get_or_404(reserva_id)
    propiedad = reserva.propiedad
    ahora = datetime.utcnow().date()
    dias_antes = (reserva.fecha_inicio - ahora).days
    pagos = Pago.query.filter_by(reserva_id=reserva.id).all()
    porcentaje = propiedad.porcentaje_pago_reserva

    # Cambiar pagos pendientes a cancelados antes de cancelar la reserva
    for pago in pagos:
        if pago.status == 'pending':
            pago.status = 'cancelled'
    
    # Cambiar estado de la reserva a cancelada
    reserva.estado = 'cancelada'
    db.session.commit()

    # Mensajes claros según reglas de negocio
    if not propiedad.reembolsable:
        mensaje_reembolso = 'Cancelación exitosa. No se realiza reembolso porque la propiedad no es reembolsable.'
    elif dias_antes < 2 and int(porcentaje) == 100:
        mensaje_reembolso = 'Cancelación exitosa. No se realiza reembolso porque la cancelación fue con menos de 48 horas de anticipación.'
    elif int(porcentaje) == 20:
        mensaje_reembolso = 'Cancelación exitosa. No se realiza reembolso porque solo se abonó el 20% de reserva.'
    elif int(porcentaje) == 100:
        mensaje_reembolso = 'Cancelación con reembolso exitosa. Se reembolsa el 20% del pago anticipado.'
    else:
        mensaje_reembolso = 'Cancelación exitosa.'

    flash(mensaje_reembolso, 'success')
    return redirect(url_for('main.reservas_futuras'))

@main.route('/mis-pagos')
@login_required
def mis_pagos():
    user_controller = UserController()
    return user_controller.ver_pagos_cliente(session)

@main.route('/ver-pago/<int:reserva_id>')
def ver_pago_reserva(reserva_id):
    from models.reserva import Reserva
    from models.pago import Pago
    from datetime import datetime, timedelta
    reserva = Reserva.query.get_or_404(reserva_id)
    pagos = reserva.pagos
    pagos_vista = []
    for pago in pagos:
        pago_dict = pago.__dict__.copy()
        # Mostrar el estado real del pago
        pago_dict['status'] = pago.status
        pagos_vista.append(pago_dict)
    return render_template('detalle_pago.html', reserva=reserva, pagos=pagos_vista, timedelta=timedelta)

@main.route('/reservas/canceladas')
def reservas_canceladas():
    reservas = user_controller.obtener_reservas_canceladas(session)
    current_date = datetime.now().date()
    return render_template('reservas_canceladas.html', reservas=reservas, current_date=current_date)

@main.route('/propiedad/<int:propiedad_id>/inhabilitar', methods=['GET'])
@login_required
def inhabilitar_propiedad_form(propiedad_id):
    if session.get('rol') not in ['administrador', 'superusuario', 'encargado']:
        flash('No tienes permisos para inhabilitar propiedades.', 'danger')
        return redirect(url_for('main.index'))
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    if session.get('rol') == 'encargado' and propiedad.encargado_id != session.get('user_id'):
        flash('Solo puedes inhabilitar propiedades que tienes asignadas.', 'danger')
        return redirect(url_for('main.index'))
    propiedad_controller = PropiedadController()
    return propiedad_controller.inhabilitar_propiedad_form(request, session, propiedad_id)

@main.route('/propiedad/<int:propiedad_id>/inhabilitar', methods=['POST'])
@login_required
def inhabilitar_propiedad(propiedad_id):
    if session.get('rol') not in ['administrador', 'superusuario', 'encargado']:
        flash('No tienes permisos para inhabilitar propiedades.', 'danger')
        return redirect(url_for('main.index'))
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    if session.get('rol') == 'encargado' and propiedad.encargado_id != session.get('user_id'):
        flash('Solo puedes inhabilitar propiedades que tienes asignadas.', 'danger')
        return redirect(url_for('main.index'))
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    accion_reserva = request.form.get('accion_reserva')
    if not fecha_inicio or not fecha_fin:
        flash('Debe seleccionar un rango de fechas.', 'danger')
        return redirect(url_for('main.inhabilitar_propiedad_form', propiedad_id=propiedad_id))
    propiedad_controller = PropiedadController()
    resultado, mensaje, tipo = propiedad_controller.inhabilitar_propiedad(
        propiedad_id, fecha_inicio, fecha_fin, accion_reserva, session
    )
    if resultado == 'upgrade':
        return redirect(url_for('main.upgrade_reservas'))
    elif resultado is True:
        flash(mensaje, tipo)
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    else:
        flash(mensaje, tipo)
        return redirect(url_for('main.inhabilitar_propiedad_form', propiedad_id=propiedad_id))

@main.route('/upgrade_reservas', methods=['GET', 'POST'])
@login_required
def upgrade_reservas():
    if session.get('rol') not in ['administrador', 'superusuario', 'encargado']:
        flash('No tienes permisos para realizar upgrades de reservas.', 'danger')
        return redirect(url_for('main.index'))
    propiedad_controller = PropiedadController()
    return propiedad_controller.upgrade_reservas(request, session)

@main.route('/propiedad/ocupar/<int:propiedad_id>', methods=['GET'])
@login_required
def ocupar_propiedad_form(propiedad_id):
    from architectural_patterns.controller.propiedad_controller import PropiedadController
    return PropiedadController().ocupar_propiedad_form(request, session, propiedad_id)

# Check-outs pendientes para encargado
@main.route('/check-outs-pendientes')
def check_outs_pendientes():
    from models.reserva import Reserva
    from models.propiedad import Propiedad
    from models.user import Cliente
    from database import db
    if not (session.get('rol') == 'encargado' and session.get('user_id')):
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))
    encargado_id = session.get('user_id')
    # Propiedades asignadas al encargado
    propiedades = Propiedad.query.filter_by(encargado_id=encargado_id, eliminado=False).all()
    propiedad_ids = [p.id for p in propiedades]
    # Reservas concretadas, finalizadas, sin checkout realizado
    reservas = Reserva.query.filter(
        Reserva.propiedad_id.in_(propiedad_ids),
        Reserva.estado == 'concretada',
        Reserva.fecha_fin < db.func.current_date(),
        (Reserva.checkout_realizado == False)
    ).all()
    return render_template('check_outs_pendientes.html', reservas=reservas)

# Ruta para realizar checkout de una reserva
@main.route('/realizar-checkout/<int:reserva_id>', methods=['POST'])
def realizar_checkout(reserva_id):
    from models.reserva import Reserva
    from models.propiedad import Propiedad
    from database import db
    reserva = Reserva.query.get_or_404(reserva_id)
    checkout_estado = request.form.get('checkout_estado', '').strip()
    reserva.checkout_realizado = True
    reserva.checkout_estado = checkout_estado
    db.session.commit()
    # Si el checkbox de inhabilitar propiedad está marcado, redirigir al detalle de la propiedad
    if request.form.get('inhabilitar_propiedad'):
        flash('Check-out realizado.', 'success')
        return redirect(url_for('main.detalle_propiedad', id=reserva.propiedad_id))
    # Si no, recargar la página de check-outs pendientes
    flash('Check-out realizado.', 'success')
    return redirect(url_for('main.check_outs_pendientes'))

@main.route('/api/usuarios_info', methods=['POST'])
@login_required
def api_usuarios_info():
    data = request.get_json()
    ids = data.get('ids', [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({'error': 'Formato de datos inválido'}), 400
    from models.user import Usuario
    usuarios = Usuario.query.filter(Usuario.id.in_(ids)).all()
    usuarios_info = [
        {
            'id': u.id,
            'nombre': u.nombre,
            'apellido': u.apellido
        } for u in usuarios
    ]
    return jsonify({'usuarios': usuarios_info})