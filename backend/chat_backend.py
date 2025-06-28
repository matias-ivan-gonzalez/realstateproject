

from flask import session
from flask_socketio import emit, join_room
from models.mensaje_chat import MensajeChat
from database import db

def is_admin():
    return session.get('rol') in ['administrador', 'superusuario']

def is_cliente():
    return session.get('rol') == 'cliente'




def register_chat_events(socketio):

    @socketio.on('cliente_mensaje')
    def handle_cliente_mensaje(data):
        if not is_cliente():
            return
        user = data.get('user') or session.get('nombre') or 'Cliente'
        rol = session.get('rol') or 'cliente'
        print(f"[SOCKET] Mensaje recibido del cliente: user={user}, rol={rol}, data={data}")
        mensaje = MensajeChat(user=user, rol=rol, msg=data['msg'])
        db.session.add(mensaje)
        db.session.commit()
        emit('chat_mensaje', mensaje.to_dict(), broadcast=True)

    @socketio.on('admin_mensaje')
    def handle_admin_mensaje(data):
        if not is_admin():
            return
        user = data.get('user') or session.get('nombre') or 'Admin'
        rol = session.get('rol') or 'administrador'
        print(f"[SOCKET] Mensaje recibido del admin: user={user}, rol={rol}, data={data}")
        mensaje = MensajeChat(user=user, rol=rol, msg=data['msg'])
        db.session.add(mensaje)
        db.session.commit()
        emit('chat_mensaje', mensaje.to_dict(), broadcast=True)
    @socketio.on('get_chat_history')
    def handle_get_chat_history():
        mensajes = MensajeChat.query.order_by(MensajeChat.timestamp.asc()).all()
        emit('chat_history', [m.to_dict() for m in mensajes])

    @socketio.on('join_admins')
    def join_admins():
        if is_admin():
            join_room('admins')
