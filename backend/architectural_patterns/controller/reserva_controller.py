from models.reserva import Reserva
from models.user import Cliente
from models.propiedad import Propiedad
from models.pago import Pago
from database import db
from datetime import datetime, timedelta
from flask import redirect, url_for, flash, jsonify
import mercadopago
from config import MERCADOPAGO_ACCESS_TOKEN
import os

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
                cantidad_personas=cantidad_huespedes,
                reembolsable=propiedad.reembolsable
            )
            db.session.add(reserva)
            db.session.commit()
            # Calcular el monto del pago según el porcentaje de la propiedad
            dias = (fecha_fin_dt - fecha_inicio_dt).days + 1
            if dias < 1:
                dias = 1
            monto_total = float(propiedad.precio * dias)
            porcentaje = propiedad.porcentaje_pago_reserva
            fecha_cobro_total = fecha_inicio_dt
            print(f"[DEBUG] porcentaje_pago_reserva: {porcentaje} (type: {type(porcentaje)})")
            print(f"[DEBUG] fecha_cobro_total: {fecha_cobro_total}")
            if int(porcentaje) == 20:
                # Pago del 20% (pagado)
                monto_adelanto = round(monto_total * 0.2, 2)
                if monto_adelanto < 1:
                    monto_adelanto = 1
                pago_adelanto = Pago(
                    monto=monto_adelanto,
                    reserva_id=reserva.id,
                    fecha_emision=datetime.utcnow(),
                    status='paid',
                    fecha_cobro_total=datetime.utcnow()
                )
                db.session.add(pago_adelanto)
                # Pago del 80% (pendiente)
                monto_restante = round(monto_total * 0.8, 2)
                if monto_restante < 1:
                    monto_restante = 1
                fecha_cobro_pending = fecha_inicio_dt - timedelta(days=2)
                pago_restante = Pago(
                    monto=monto_restante,
                    reserva_id=reserva.id,
                    fecha_emision=None,
                    status='pending',
                    fecha_cobro_total=fecha_cobro_pending
                )
                db.session.add(pago_restante)
            elif int(porcentaje) == 0:
                print("[DEBUG] Creando pago pending 100% para porcentaje 0%")
                # Pago pendiente por el 100%
                fecha_cobro_pending = fecha_inicio_dt - timedelta(days=2)
                pago_pendiente = Pago(
                    monto=monto_total,
                    reserva_id=reserva.id,
                    fecha_emision=None,
                    status='pending',
                    fecha_cobro_total=fecha_cobro_pending
                )
                db.session.add(pago_pendiente)
            elif int(porcentaje) == 100:
                # Pago completo, pagado
                pago_total = Pago(
                    monto=monto_total,
                    reserva_id=reserva.id,
                    fecha_emision=datetime.utcnow(),
                    status='paid',
                    fecha_cobro_total=datetime.utcnow()
                )
                db.session.add(pago_total)
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
            cantidad_personas=cantidad_huespedes,
            reembolsable=propiedad.reembolsable
        )
        db.session.add(reserva)
        db.session.commit()

        # Crear pago pending 100% para reservas con 0%
        if int(porcentaje) == 0:
            monto_total = float(propiedad.precio * noches)
            fecha_cobro_total = fecha_inicio_dt - timedelta(days=2)
            pago_pendiente = Pago(
                monto=monto_total,
                reserva_id=reserva.id,
                fecha_emision=None,
                status='pending',
                fecha_cobro_total=fecha_cobro_total
            )
            db.session.add(pago_pendiente)
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
            dias = (datetime.strptime(fecha_fin, '%Y-%m-%d') - datetime.strptime(fecha_inicio, '%Y-%m-%d')).days + 1
            if dias < 1:
                dias = 1
            monto_total = float(propiedad.precio * dias)
            porcentaje = propiedad.porcentaje_pago_reserva
            monto_a_pagar = round(monto_total * (porcentaje / 100), 2) if porcentaje > 0 else monto_total
            sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
            base_url = os.environ.get("BASE_URL")
            preference_data = {
                "items": [
                    {
                        "title": f"Reserva de {propiedad.nombre}",
                        "quantity": 1,
                        "currency_id": "ARS",
                        "unit_price": monto_a_pagar
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
        # Siempre NO requiere pago inmediato
        requiere_pago = False

        noches_adicionales = (nueva_fecha_fin_dt - reserva.fecha_fin).days
        if noches_adicionales < 1:
            return jsonify({'error': 'Debes seleccionar al menos una noche adicional'}), 400
        monto_total = float(propiedad.precio * noches_adicionales)
        porcentaje = propiedad.porcentaje_pago_reserva if requiere_pago else 0
        monto_a_cobrar = round(monto_total * (porcentaje / 100), 2) if porcentaje > 0 else monto_total

        # Nunca entra a Mercado Pago, siempre genera pago pendiente
        reserva.fecha_fin = nueva_fecha_fin_dt
        db.session.commit()

        # Crear pago pendiente por la extensión
        if noches_adicionales > 0 and monto_total > 0:
            from models.pago import Pago
            pago_ext = Pago(
                monto=monto_total,
                reserva_id=reserva.id,
                fecha_emision=datetime.utcnow(),
                status='pending',
                fecha_cobro_total=None
            )
            db.session.add(pago_ext)
            db.session.commit()

        session['show_extension_flash'] = True
        return jsonify({'success': True})
