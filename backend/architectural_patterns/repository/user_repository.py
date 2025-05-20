from models.user import Usuario, Cliente, Administrador, Encargado, SuperUsuario
from database import db

class UserRepository:
    def get_by_id(self, user_id):
        return Usuario.query.get(user_id)

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
        elif tipo == 'superusuario':
            nuevo_usuario = SuperUsuario(**user_dict)
        else:
            nuevo_usuario = Usuario(**user_dict)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario

    def update_user(self, user_id, user_dict):
        user = Usuario.query.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Actualizar los campos del usuario
        for key, value in user_dict.items():
            setattr(user, key, value)
        
        db.session.commit()
        return user 