from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from models.propiedad import Propiedad
from sqlalchemy.sql.expression import func
from architectural_patterns.controller.user_controller import UserController
from architectural_patterns.controller.empleado_controller import EmpleadoController
from architectural_patterns.controller.propiedad_controller import PropiedadController
from architectural_patterns.controller.busqueda_controller import SearchController
import os
from datetime import datetime, date
from models.calificacion import Calificacion
from models.reserva import Reserva
from models.user import Cliente
from database import db
from config import MERCADOPAGO_ACCESS_TOKEN
import mercadopago

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

@main.route('/propiedad/<int:propiedad_id>/reservar', methods=['POST'])
@login_required
def reservar_propiedad(propiedad_id):
    propiedad = Propiedad.query.get_or_404(propiedad_id)
    cliente = Cliente.query.get(session['user_id'])
    if not cliente:
        flash('Usuario no válido.', 'danger')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

    # Obtener datos del formulario
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    cantidad_huespedes = int(request.form.get('huespedes', 1))

    # Validar fechas y huéspedes
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        if fecha_fin_dt <= fecha_inicio_dt:
            flash('La fecha de fin debe ser posterior a la de inicio.', 'danger')
            return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    except Exception:
        flash('Fechas inválidas.', 'danger')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    if cantidad_huespedes < 1 or cantidad_huespedes > propiedad.limite_personas:
        flash('Cantidad de huéspedes fuera de rango.', 'danger')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    reservas_solapadas = Reserva.query.filter(
        Reserva.propiedad_id == propiedad_id,
        Reserva.fecha_fin > fecha_inicio_dt,
        Reserva.fecha_inicio < fecha_fin_dt
    ).all()
    if reservas_solapadas:
        flash('Reserva fallida por indisponibilidad de la propiedad', 'danger')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

    noches = (fecha_fin_dt - fecha_inicio_dt).days
    if noches < 1:
        noches = 1
    porcentaje = propiedad.porcentaje_pago_reserva
    if porcentaje > 0:
        flash('El pago debe realizarse a través de Checkout Pro.', 'danger')
        return redirect(url_for('main.detalle_propiedad', id=propiedad_id))
    else:
        mensaje_pago = 'Reserva exitosa 0% abonado'

    reserva = Reserva(
        cliente_id=cliente.id,
        propiedad_id=propiedad.id,
        fecha_inicio=fecha_inicio_dt,
        fecha_fin=fecha_fin_dt,
        cantidad_personas=cantidad_huespedes
    )
    db.session.add(reserva)
    db.session.commit()
    flash(mensaje_pago, 'success')
    return redirect(url_for('main.detalle_propiedad', id=propiedad_id))

@main.route('/crear_preferencia_checkout', methods=['POST'])
@login_required
def crear_preferencia_checkout():
    try:
        data = request.get_json()
        propiedad_id = int(data['propiedad_id'])
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']
        cantidad_huespedes = int(data['huespedes'])
        propiedad = Propiedad.query.get_or_404(propiedad_id)
        noches = (datetime.strptime(fecha_fin, '%Y-%m-%d') - datetime.strptime(fecha_inicio, '%Y-%m-%d')).days
        if noches < 1:
            noches = 1
        monto_total = float(propiedad.precio * noches)
        porcentaje = propiedad.porcentaje_pago_reserva
        monto_a_cobrar = round(monto_total * (porcentaje / 100), 2)
        if monto_a_cobrar < 1:
            monto_a_cobrar = 1
        sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
        base_url = "https://liked-indirectly-finch.ngrok-free.app"
        preference_data = {
            "items": [
                {
                    "title": f"Reserva de {propiedad.nombre}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": monto_a_cobrar
                }
            ],
            "back_urls": {
                "success": f"{base_url}/propiedad/{propiedad_id}?pago=success&fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}&huespedes={cantidad_huespedes}",
                "failure": f"{base_url}/propiedad/{propiedad_id}?pago=failure",
                "pending": f"{base_url}/propiedad/{propiedad_id}?pago=pending"
            },
            "auto_return": "approved",
            "binary_mode": True
        }
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        print("Respuesta de Mercado Pago:", preference)  # Log para depuración
        if "init_point" in preference:
            # Crear la reserva en la base de datos aquí
            from models.reserva import Reserva
            from models.user import Cliente
            from database import db
            cliente = Cliente.query.get(session['user_id'])
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Verificar que no exista ya una reserva igual
            reserva_existente = Reserva.query.filter_by(
                cliente_id=cliente.id,
                propiedad_id=propiedad.id,
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt
            ).first()
            if not reserva_existente:
                reserva = Reserva(
                    cliente_id=cliente.id,
                    propiedad_id=propiedad.id,
                    fecha_inicio=fecha_inicio_dt,
                    fecha_fin=fecha_fin_dt,
                    cantidad_personas=cantidad_huespedes
                )
                db.session.add(reserva)
                db.session.commit()
            return jsonify(init_point=preference["init_point"])
        else:
            print("Error al crear preferencia:", preference)
            return jsonify({"error": "No se pudo crear la preferencia de pago", "detalle": preference}), 400
    except Exception as e:
        import traceback
        print("Excepción en crear_preferencia_checkout:", e)
        traceback.print_exc()
        return jsonify({"error": "Error interno en el servidor", "detalle": str(e)}), 500
