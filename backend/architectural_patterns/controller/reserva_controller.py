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
        from flask import session
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
            # Setear bandera para mostrar flash message en la vista
            session['show_reserva_exitosa_flash'] = propiedad.porcentaje_pago_reserva
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
                "binary_mode": True,
                "payment_methods": {
                    "excluded_payment_types": [
                        {"id": "debit_card"},
                        {"id": "ticket"},
                        {"id": "atm"},
                        {"id": "prepaid_card"}
                    ],
                    "excluded_payment_methods": [
                        {"id": "amex"},
                        {"id": "naranja"},
                        {"id": "cabal"},
                        {"id": "argencard"},
                        {"id": "cencosud"},
                        {"id": "tarshop"},
                        {"id": "diners"},
                        {"id": "pagofacil"},
                        {"id": "rapipago"},
                        {"id": "cmr"},
                        {"id": "cordobesa"},
                        {"id": "maestro"},
                        {"id": "mercadopago"},
                        {"id": "pagoefectivo"},
                        {"id": "visa_debit"},
                        {"id": "master_debit"},
                        {"id": "debmaster"},
                        {"id": "debvisa"}
                    ],
                    "installments": 1
                },
                "payer": {
                    "email": session.get("email", "")
                }
            }
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            print("Respuesta de Mercado Pago:", preference)  # Log para depuración
            if "init_point" in preference:
                # No crear la reserva aquí
                return jsonify(init_point=preference["init_point"])
            else:
                print("Error al crear preferencia:", preference)
                session['show_reserva_fallida_flash'] = True
                return jsonify({"error": "No se pudo crear la preferencia de pago", "detalle": preference}), 400
        except Exception as e:
            import traceback
            print("Excepción en crear_preferencia_checkout:", e)
            traceback.print_exc()
            session['show_reserva_fallida_flash'] = True
            return jsonify({"error": "Error interno en el servidor", "detalle": str(e)}), 500

    def extender_reserva(self, session, reserva_id, nueva_fecha_fin_dt):
        from flask import jsonify
        from datetime import timedelta
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            return jsonify({'error': 'Reserva no encontrada'}), 404
        propiedad = reserva.propiedad
        hoy = datetime.now().date()
        # Regla 1: Solo puede extenderse hasta como mínimo dos días antes de la fecha de salida prevista
        if (reserva.fecha_fin - hoy).days < 2:
            return jsonify({'error': 'Solo puedes extender la reserva hasta 2 días antes de la fecha de salida'}), 400
        # La nueva fecha debe ser posterior a la actual
        if nueva_fecha_fin_dt <= reserva.fecha_fin:
            return jsonify({'error': 'La nueva fecha de salida debe ser posterior a la actual'}), 400
        # Verificar disponibilidad (no debe haber reservas solapadas ni ocupaciones)
        from architectural_patterns.repository.reserva_repository import ReservaRepository
        repo = ReservaRepository()
        reservas_solapadas = Reserva.query.filter(
            Reserva.propiedad_id == propiedad.id,
            Reserva.id != reserva.id,
            Reserva.fecha_fin > reserva.fecha_fin,
            Reserva.fecha_inicio < nueva_fecha_fin_dt
        ).all()
        # Validar ocupaciones
        from models.ocupacion import Ocupacion
        ocupaciones_solapadas = Ocupacion.query.filter(
            Ocupacion.propiedad_id == propiedad.id,
            Ocupacion.fecha_fin > reserva.fecha_fin,
            Ocupacion.fecha_inicio < nueva_fecha_fin_dt
        ).all()
        if reservas_solapadas or ocupaciones_solapadas:
            return jsonify({'error': 'Reserva fallida por indisponibilidad de la propiedad'}), 400
        # Regla 2: Si faltan 2 días o menos para el inicio, o ya comenzó, debe abonar inmediatamente
        requiere_pago = False
        if (reserva.fecha_inicio - hoy).days <= 2 or hoy >= reserva.fecha_inicio:
            requiere_pago = True
        noches_adicionales = (nueva_fecha_fin_dt - reserva.fecha_fin).days
        if noches_adicionales < 1:
            return jsonify({'error': 'Debes seleccionar al menos una noche adicional'}), 400
        monto_total = float(propiedad.precio * noches_adicionales)
        porcentaje = propiedad.porcentaje_pago_reserva if requiere_pago else 0
        monto_a_cobrar = round(monto_total * (porcentaje / 100), 2) if porcentaje > 0 else monto_total
        if requiere_pago and monto_a_cobrar > 0:
            # Mercado Pago
            sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
            base_url = "https://liked-indirectly-finch.ngrok-free.app"
            preference_data = {
                "items": [
                    {
                        "title": f"Extensión de reserva de {propiedad.nombre}",
                        "quantity": 1,
                        "currency_id": "ARS",
                        "unit_price": monto_a_cobrar
                    }
                ],
                "back_urls": {
                    "success": f"{base_url}/extender_reserva_success?reserva_id={reserva.id}&nueva_fecha_fin={nueva_fecha_fin_dt}",
                    "failure": f"{base_url}/extender_reserva_failure",
                    "pending": f"{base_url}/extender_reserva_pending"
                },
                "auto_return": "approved",
                "binary_mode": True,
                "payment_methods": {
                    "excluded_payment_types": [
                        {"id": "debit_card"},
                        {"id": "ticket"},
                        {"id": "atm"},
                        {"id": "prepaid_card"}
                    ],
                    "excluded_payment_methods": [
                        {"id": "amex"},
                        {"id": "naranja"},
                        {"id": "cabal"},
                        {"id": "argencard"},
                        {"id": "cencosud"},
                        {"id": "tarshop"},
                        {"id": "diners"},
                        {"id": "pagofacil"},
                        {"id": "rapipago"},
                        {"id": "cmr"},
                        {"id": "cordobesa"},
                        {"id": "maestro"},
                        {"id": "mercadopago"},
                        {"id": "pagoefectivo"},
                        {"id": "visa_debit"},
                        {"id": "master_debit"},
                        {"id": "debmaster"},
                        {"id": "debvisa"}
                    ],
                    "installments": 1
                },
                "payer": {
                    "email": session.get("email", "")
                }
            }
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            if "init_point" in preference:
                return jsonify(init_point=preference["init_point"])
            else:
                return jsonify({"error": "No se pudo crear la preferencia de pago"}), 400
        # Si no requiere pago, actualizar la reserva directamente
        reserva.fecha_fin = nueva_fecha_fin_dt
        db.session.commit()
        return jsonify({'success': True})
