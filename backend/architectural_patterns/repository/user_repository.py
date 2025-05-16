from models.user import Cliente
from database import db

class UserRepository:
    def get_by_email(self, email):
        return Cliente.query.filter_by(email=email).first()

    def get_by_dni(self, dni):
        return Cliente.query.filter_by(dni=dni).first()

    def create_cliente(self, user_dict):
        nuevo_cliente = Cliente(**user_dict)
        db.session.add(nuevo_cliente)
        db.session.commit()
        return nuevo_cliente 