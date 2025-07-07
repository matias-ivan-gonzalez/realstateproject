

from flask import session
from flask_socketio import emit, join_room
from models.mensaje_chat import MensajeChat
from models.conversacion import Conversacion
from database import db

def is_admin():
    return session.get('rol') in ['administrador', 'superusuario']

def is_cliente():
    return session.get('rol') == 'cliente'




def register_chat_events(socketio):
    @socketio.on('listar_conversaciones')
    def listar_conversaciones():
        if not is_admin():
            emit('conversaciones_list', [])
            return
        from models.conversacion import Conversacion
        from models.user import Cliente
        conversaciones = Conversacion.query.order_by(Conversacion.fecha_creacion.desc()).all()
        data = []
        for c in conversaciones:
            cliente_nombre = None
            try:
                cliente = Cliente.query.get(c.cliente_id)
                if cliente:
                    cliente_nombre = f"{cliente.nombre} {cliente.apellido}".strip()
            except Exception:
                cliente_nombre = None
            data.append({
                'id': c.id,
                'cliente_id': c.cliente_id,
                'cliente_nombre': cliente_nombre,
                'fecha_creacion': c.fecha_creacion.isoformat(),
                'estado': c.estado
            })
        emit('conversaciones_list', data)

    @socketio.on('cliente_mensaje')
    def handle_cliente_mensaje(data):
        if not is_cliente():
            return
        user = data.get('user') or session.get('nombre') or 'Cliente'
        rol = session.get('rol') or 'cliente'
        cliente_id = session.get('user_id')
        reserva_id = data.get('reserva_id')
        tipo = data.get('tipo')  # 'futuro' o 'curso'
        if not reserva_id or not tipo:
            print('[SOCKET] cliente_mensaje: falta reserva_id o tipo')
            return
        # Buscar o crear la conversación única de este cliente para esa reserva y tipo
        conversacion = Conversacion.query.filter_by(cliente_id=cliente_id, reserva_id=reserva_id, tipo=tipo, estado='abierta').first()
        if not conversacion:
            conversacion = Conversacion(cliente_id=cliente_id, reserva_id=reserva_id, tipo=tipo)
            db.session.add(conversacion)
            db.session.commit()
        print(f"[SOCKET] Mensaje recibido del cliente: user={user}, rol={rol}, cliente_id={cliente_id}, reserva_id={reserva_id}, tipo={tipo}, data={data}")
        mensaje = MensajeChat(user=user, rol=rol, msg=data['msg'], conversacion_id=conversacion.id)
        db.session.add(mensaje)
        db.session.commit()
        emit('chat_mensaje', mensaje.to_dict(), room=f'chat_{conversacion.id}')
        # Si es el primer mensaje de la conversación, responder automáticamente como admin
        mensajes_previos = MensajeChat.query.filter_by(conversacion_id=conversacion.id).count()
        if mensajes_previos == 1:
            auto_msg = MensajeChat(
                user='Alquilando',
                rol='administrador',
                msg='Gracias por contactarnos, en un momento estamos con usted.',
                conversacion_id=conversacion.id
            )
            db.session.add(auto_msg)
            db.session.commit()
            emit('chat_mensaje', auto_msg.to_dict(), room=f'chat_{conversacion.id}')

    @socketio.on('admin_mensaje')
    def handle_admin_mensaje(data):
        user = data.get('user') or session.get('nombre') or 'Admin'
        rol = session.get('rol') or 'administrador'
        conversacion_id = data.get('conversacion_id')
        if not conversacion_id:
            print('[SOCKET] admin_mensaje: conversacion_id faltante')
            return
        conversacion = Conversacion.query.get(conversacion_id)
        if not conversacion:
            print('[SOCKET] admin_mensaje: conversacion no encontrada')
            return
        # --- NUEVO: Solo permitir admins si NO hay encargado asignado ---
        if conversacion.tipo == 'curso':
            from models.reserva import Reserva
            from models.propiedad import Propiedad
            reserva = Reserva.query.get(conversacion.reserva_id)
            encargado_id = None
            if reserva:
                propiedad = Propiedad.query.get(reserva.propiedad_id)
                if propiedad:
                    encargado_id = getattr(propiedad, 'encargado_id', None)
            if encargado_id:
                # Si hay encargado, los admins no pueden enviar mensajes
                print('[SOCKET] admin_mensaje: Hay encargado asignado, solo el encargado puede responder')
                return
        if not is_admin():
            return
        print(f"[SOCKET] Mensaje recibido del admin: user={user}, rol={rol}, conversacion_id={conversacion_id}, data={data}")
        mensaje = MensajeChat(user=user, rol=rol, msg=data['msg'], conversacion_id=conversacion.id)
        db.session.add(mensaje)
        db.session.commit()
        emit('chat_mensaje', mensaje.to_dict(), room=f'chat_{conversacion.id}')
    @socketio.on('encargado_mensaje')
    def handle_encargado_mensaje(data):
        # Solo el encargado de la propiedad puede enviar mensajes en curso
        if session.get('rol') != 'encargado':
            return
        user = data.get('user') or session.get('nombre') or 'Encargado'
        rol = session.get('rol') or 'encargado'
        conversacion_id = data.get('conversacion_id')
        if not conversacion_id:
            print('[SOCKET] encargado_mensaje: conversacion_id faltante')
            return
        conversacion = Conversacion.query.get(conversacion_id)
        if not conversacion:
            print('[SOCKET] encargado_mensaje: conversacion no encontrada')
            return
        if conversacion.tipo != 'curso':
            print('[SOCKET] encargado_mensaje: Solo puede responder en conversaciones en curso')
            return
        from models.reserva import Reserva
        from models.propiedad import Propiedad
        reserva = Reserva.query.get(conversacion.reserva_id)
        encargado_id = None
        if reserva:
            propiedad = Propiedad.query.get(reserva.propiedad_id)
            if propiedad:
                encargado_id = getattr(propiedad, 'encargado_id', None)
        if encargado_id != session.get('user_id'):
            print('[SOCKET] encargado_mensaje: No es el encargado asignado a esta propiedad')
            return
        mensaje = MensajeChat(user=user, rol=rol, msg=data['msg'], conversacion_id=conversacion.id)
        db.session.add(mensaje)
        db.session.commit()
        emit('chat_mensaje', mensaje.to_dict(), room=f'chat_{conversacion.id}')
    @socketio.on('get_chat_history')
    def handle_get_chat_history(data=None):
        # Soporte para merge de chats (futuro y curso) de una reserva
        conversacion_id = None
        conversacion = None
        merge = data.get('merge') if data else False
        if merge:
            cliente_id = session.get('user_id')
            reserva_id = data.get('reserva_id') if data else None
            if not reserva_id:
                emit('chat_history', [])
                return
            # Buscar ambas conversaciones (futuro y curso) de la reserva
            convs = Conversacion.query.filter_by(cliente_id=cliente_id, reserva_id=reserva_id).all()
            mensajes = []
            for conv in convs:
                mensajes += MensajeChat.query.filter_by(conversacion_id=conv.id).all()
            # Ordenar todos los mensajes por timestamp
            mensajes.sort(key=lambda m: m.timestamp)
            emit('chat_history', [m.to_dict() for m in mensajes])
            return
        if (is_admin() or session.get('rol') == 'encargado') and data and data.get('conversacion_id'):
            conversacion_id = data['conversacion_id']
            conversacion = Conversacion.query.get(conversacion_id)
        else:
            cliente_id = session.get('user_id')
            reserva_id = None
            tipo = None
            if data:
                reserva_id = data.get('reserva_id')
                tipo = data.get('tipo')
            if not reserva_id or not tipo:
                emit('chat_history', [])
                return
            # Buscar conversación sin importar el estado (abierta o cerrada)
            conversacion = Conversacion.query.filter_by(cliente_id=cliente_id, reserva_id=reserva_id, tipo=tipo).first()
            if conversacion:
                conversacion_id = conversacion.id
        if conversacion_id:
            mensajes = MensajeChat.query.filter_by(conversacion_id=conversacion_id).order_by(MensajeChat.timestamp.asc()).all()
            emit('chat_history', [m.to_dict() for m in mensajes])
        else:
            emit('chat_history', [])

    @socketio.on('join_chat')
    def join_chat(data):
        # Un cliente, admin o encargado se une a su room de conversación
        if (is_admin() or session.get('rol') == 'encargado') and data and data.get('conversacion_id'):
            join_room(f"chat_{data['conversacion_id']}")
        elif is_cliente():
            cliente_id = session.get('user_id')
            reserva_id = None
            tipo = None
            if data:
                reserva_id = data.get('reserva_id')
                tipo = data.get('tipo')
            if not reserva_id or not tipo:
                return
            conversacion = Conversacion.query.filter_by(cliente_id=cliente_id, reserva_id=reserva_id, tipo=tipo, estado='abierta').first()
            if conversacion:
                join_room(f"chat_{conversacion.id}")
