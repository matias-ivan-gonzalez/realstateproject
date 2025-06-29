

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
        # Buscar o crear la conversación única de este cliente
        conversacion = Conversacion.query.filter_by(cliente_id=cliente_id, estado='abierta').first()
        if not conversacion:
            conversacion = Conversacion(cliente_id=cliente_id)
            db.session.add(conversacion)
            db.session.commit()
        print(f"[SOCKET] Mensaje recibido del cliente: user={user}, rol={rol}, cliente_id={cliente_id}, data={data}")
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
        if not is_admin():
            return
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
        print(f"[SOCKET] Mensaje recibido del admin: user={user}, rol={rol}, conversacion_id={conversacion_id}, data={data}")
        mensaje = MensajeChat(user=user, rol=rol, msg=data['msg'], conversacion_id=conversacion.id)
        db.session.add(mensaje)
        db.session.commit()
        emit('chat_mensaje', mensaje.to_dict(), room=f'chat_{conversacion.id}')
    @socketio.on('get_chat_history')
    def handle_get_chat_history(data=None):
        # El cliente siempre pide su propia conversación, el admin puede pedir la de un cliente específico
        conversacion_id = None
        if is_admin() and data and data.get('conversacion_id'):
            conversacion_id = data['conversacion_id']
        else:
            cliente_id = session.get('user_id')
            conversacion = Conversacion.query.filter_by(cliente_id=cliente_id, estado='abierta').first()
            if conversacion:
                conversacion_id = conversacion.id
        if conversacion_id:
            mensajes = MensajeChat.query.filter_by(conversacion_id=conversacion_id).order_by(MensajeChat.timestamp.asc()).all()
            emit('chat_history', [m.to_dict() for m in mensajes])
        else:
            emit('chat_history', [])

    @socketio.on('join_chat')
    def join_chat(data):
        # Un cliente se une a su room de conversación, un admin puede unirse a la conversación de un cliente
        if is_admin() and data and data.get('conversacion_id'):
            join_room(f"chat_{data['conversacion_id']}")
        elif is_cliente():
            cliente_id = session.get('user_id')
            conversacion = Conversacion.query.filter_by(cliente_id=cliente_id, estado='abierta').first()
            if conversacion:
                join_room(f"chat_{conversacion.id}")
