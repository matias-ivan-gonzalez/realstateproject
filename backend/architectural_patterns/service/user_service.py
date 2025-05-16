from architectural_patterns.repository.user_repository import UserRepository
from werkzeug.security import generate_password_hash
from datetime import datetime

class UserService:
    def __init__(self, user_repository=None):
        self.user_repository = user_repository or UserRepository()

    def email_exists(self, email):
        return self.user_repository.get_by_email(email) is not None

    def dni_exists(self, dni):
        return self.user_repository.get_by_dni(dni) is not None

    def parse_fecha_nacimiento(self, f_nac):
        if not f_nac:
            return None
        try:
            return datetime.strptime(f_nac, '%Y-%m-%d').date()
        except ValueError:
            return None

    def register_user(self, data):
        # data: dict con los campos del formulario
        if self.email_exists(data['email']):
            return False, 'El email ya está registrado.'
        if self.dni_exists(data['dni']):
            return False, 'El DNI ya está registrado.'
        fecha_nacimiento = self.parse_fecha_nacimiento(data.get('f_nac'))
        if data.get('f_nac') and not fecha_nacimiento:
            return False, 'Fecha de nacimiento inválida.'
        hashed_password = generate_password_hash(data['password'])
        user_dict = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'contrasena': hashed_password,
            'telefono': data['telefono'],
            'fecha_nacimiento': fecha_nacimiento,
            'direccion': data['domicilio'],
            'nacionalidad': data['nacionalidad'],
            'dni': data['dni'],
            'tarjeta': data.get('tarjeta')
        }
        self.user_repository.create_cliente(user_dict)
        return True, 'Registro exitoso. Ahora puedes iniciar sesión.' 