
from flask import session
from flask_socketio import emit, join_room

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
        print('Mensaje recibido del cliente:', data)
        mensaje = {'user': user, 'msg': data['msg']}
        emit('chat_mensaje', mensaje, broadcast=True)

    @socketio.on('admin_mensaje')
    def handle_admin_mensaje(data):
        if not is_admin():
            return
        user = data.get('user') or session.get('nombre') or 'Admin'
        mensaje = {'user': user, 'msg': data['msg']}
        emit('chat_mensaje', mensaje, broadcast=True)

    @socketio.on('join_admins')
    def join_admins():
        if is_admin():
            join_room('admins')
