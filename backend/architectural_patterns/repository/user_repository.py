from models.user import Usuario
from database import db

class UserRepository:
    def get_by_email(self, email):
        return Usuario.query.filter_by(email=email).first()

    def get_by_dni(self, dni):
        return Usuario.query.filter_by(dni=dni).first()

    def create_usuario(self, user_dict):
        nuevo_usuario = Usuario(**user_dict)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario 