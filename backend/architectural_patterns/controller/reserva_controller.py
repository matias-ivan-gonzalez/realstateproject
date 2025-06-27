from models.reserva import Reserva
from models.user import Cliente
from models.propiedad import Propiedad
from database import db
from datetime import datetime
from flask import redirect, url_for, flash, jsonify
import mercadopago
from config import MERCADOPAGO_ACCESS_TOKEN

class ReservaController:
    def crear_reserva_checkout(self, user_id, propiedad_id, fecha_inicio, fecha_fin, cantidad_huespedes):
        cliente = Cliente.query.get(user_id)
        propiedad = Propiedad.query.get_or_404(propiedad_id)
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
            return True
        return False

    def reservar_propiedad_post(self, request, session, propiedad_id):
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

    def crear_preferencia_checkout(self, request, session):
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
                self.crear_reserva_checkout(session['user_id'], propiedad_id, fecha_inicio, fecha_fin, cantidad_huespedes)
                return jsonify(init_point=preference["init_point"])
            else:
                print("Error al crear preferencia:", preference)
                return jsonify({"error": "No se pudo crear la preferencia de pago", "detalle": preference}), 400
        except Exception as e:
            import traceback
            print("Excepción en crear_preferencia_checkout:", e)
            traceback.print_exc()
            return jsonify({"error": "Error interno en el servidor", "detalle": str(e)}), 500
