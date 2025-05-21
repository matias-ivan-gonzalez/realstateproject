from models.user import Usuario, Cliente, Administrador, Encargado, SuperUsuario
from database import db

class UserRepository:
    def get_by_id(self, user_id):
        return db.session.get(Usuario, user_id)

    def get_by_email(self, email):
        return Usuario.query.filter_by(email=email).first()

    def get_by_dni(self, dni):
        return Usuario.query.filter_by(dni=dni).first()

    def create_usuario(self, user_dict):
        tipo = user_dict.get('tipo', 'cliente')
        if tipo == 'cliente':
            nuevo_usuario = Cliente(**user_dict)
        elif tipo == 'administrador':
            nuevo_usuario = Administrador(**user_dict)
        elif tipo == 'encargado':
            nuevo_usuario = Encargado(**user_dict)
        else:  # superusuario
            nuevo_usuario = SuperUsuario(**user_dict)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario

    def update_user(self, user_id, user_dict):
        user = db.session.get(Usuario, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Actualizar los campos del usuario
        for key, value in user_dict.items():
            setattr(user, key, value)
        
        db.session.commit()
        return user

    def eliminar_usuario_logico(self, user_id):
        user = db.session.get(Usuario, user_id)
        if not user:
            return False
        user.nombre = '[eliminated]'
        user.apellido = '[eliminated]'
        user.email = f'eliminated_{user.id}@deleted.com'
        user.dni = '[eliminated]'
        user.telefono = '[eliminated]'
        if hasattr(user, 'tarjeta'):
            user.tarjeta = '[eliminated]'
        if hasattr(user, 'fecha_nacimiento'):
            user.fecha_nacimiento = None
        db.session.commit()
        return True 