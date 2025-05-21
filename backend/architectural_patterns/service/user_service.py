from architectural_patterns.repository.user_repository import UserRepository
from datetime import datetime
import re

NACIONALIDADES_VALIDAS = [
    "Afganistán", "Albania", "Alemania", "Andorra", "Angola", "Antigua y Barbuda", "Arabia Saudita", "Argelia", "Argentina", "Armenia", "Australia", "Austria", "Azerbaiyán", "Bahamas", "Bangladés", "Barbados", "Baréin", "Bélgica", "Belice", "Benín", "Bielorrusia", "Birmania", "Bolivia", "Bosnia y Herzegovina", "Botsuana", "Brasil", "Brunéi", "Bulgaria", "Burkina Faso", "Burundi", "Bután", "Cabo Verde", "Camboya", "Camerún", "Canadá", "Catar", "Chad", "Chile", "China", "Chipre", "Ciudad del Vaticano", "Colombia", "Comoras", "Corea del Norte", "Corea del Sur", "Costa de Marfil", "Costa Rica", "Croacia", "Cuba", "Dinamarca", "Dominica", "Ecuador", "Egipto", "El Salvador", "Emiratos Árabes Unidos", "Eritrea", "Eslovaquia", "Eslovenia", "España", "Estados Unidos", "Estonia", "Etiopía", "Filipinas", "Finlandia", "Fiyi", "Francia", "Gabón", "Gambia", "Georgia", "Ghana", "Granada", "Grecia", "Guatemala", "Guyana", "Guinea", "Guinea ecuatorial", "Guinea-Bisáu", "Haití", "Honduras", "Hungría", "India", "Indonesia", "Irak", "Irán", "Irlanda", "Islandia", "Islas Marshall", "Islas Salomón", "Israel", "Italia", "Jamaica", "Japón", "Jordania", "Kazajistán", "Kenia", "Kirguistán", "Kiribati", "Kuwait", "Laos", "Lesoto", "Letonia", "Líbano", "Liberia", "Libia", "Liechtenstein", "Lituania", "Luxemburgo", "Macedonia del Norte", "Madagascar", "Malasia", "Malaui", "Maldivas", "Malí", "Malta", "Marruecos", "Mauricio", "Mauritania", "México", "Micronesia", "Moldavia", "Mónaco", "Mongolia", "Montenegro", "Mozambique", "Namibia", "Nauru", "Nepal", "Nicaragua", "Níger", "Nigeria", "Noruega", "Nueva Zelanda", "Omán", "Países Bajos", "Pakistán", "Palaos", "Panamá", "Papúa Nueva Guinea", "Paraguay", "Perú", "Polonia", "Portugal", "Reino Unido", "República Centroafricana", "República Checa", "República del Congo", "República Democrática del Congo", "República Dominicana", "Ruanda", "Rumanía", "Rusia", "Samoa", "San Cristóbal y Nieves", "San Marino", "San Vicente y las Granadinas", "Santa Lucía", "Santo Tomé y Príncipe", "Senegal", "Serbia", "Seychelles", "Sierra Leona", "Singapur", "Siria", "Somalia", "Sri Lanka", "Suazilandia", "Sudáfrica", "Sudán", "Sudán del Sur", "Suecia", "Suiza", "Surinam", "Tailandia", "Tanzania", "Tayikistán", "Timor Oriental", "Togo", "Tonga", "Trinidad y Tobago", "Túnez", "Turkmenistán", "Turquía", "Tuvalu", "Ucrania", "Uganda", "Uruguay", "Uzbekistán", "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Yibuti", "Zambia", "Zimbabue"
]

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email)

def is_numeric(value):
    return value.isdigit()

class UserService:
    def __init__(self, user_repository=None):
        self.user_repository = user_repository or UserRepository()

    def get_user_by_id(self, user_id):
        return self.user_repository.get_by_id(user_id)

    def get_paises(self):
        return NACIONALIDADES_VALIDAS

    def email_exists(self, email):
        return self.user_repository.get_by_email(email)

    def dni_exists(self, dni):
        return self.user_repository.get_by_dni(dni)

    def parse_fecha_nacimiento(self, f_nac):
        if not f_nac:
            return None
        try:
            return datetime.strptime(f_nac, '%Y-%m-%d').date()
        except ValueError:
            return None

    def update_user(self, user_id, data):
        # Obtener el usuario para verificar su tipo
        user = self.get_user_by_id(user_id)
        if not user:
            return False, 'Usuario no encontrado.'

        # Campos requeridos base para todos los usuarios
        required_fields = ['nombre', 'apellido', 'email', 'telefono', 'nacionalidad', 'dni']
        
        # Agregar campos específicos de cliente si el usuario es cliente
        if user.tipo == 'cliente':
            required_fields.extend(['f_nac', 'domicilio'])

        # Validar campos requeridos
        for field in required_fields:
            if not data.get(field):
                return False, f'El campo {field} es obligatorio.'

        # Validar email
        if not is_valid_email(data['email']):
            return False, 'Email inválido.'

        # Validar campos numéricos
        if not is_numeric(data['dni']):
            return False, 'El DNI debe ser numérico.'
        if not is_numeric(data['telefono']):
            return False, 'El teléfono debe ser numérico.'
        if data.get('tarjeta') and not is_numeric(data['tarjeta']):
            return False, 'La tarjeta debe ser numérica.'

        # Validar nacionalidad
        if data['nacionalidad'] not in NACIONALIDADES_VALIDAS:
            return False, 'Nacionalidad inválida.'

        # Validar fecha de nacimiento solo si es cliente
        if user.tipo == 'cliente':
            fecha_nacimiento = self.parse_fecha_nacimiento(data.get('f_nac'))
            if not fecha_nacimiento:
                return False, 'Fecha de nacimiento inválida.'

        # Validar email y DNI duplicados solo si han cambiado
        if data['email'] != user.email:
            email_exists = self.email_exists(data['email'])
            if email_exists and email_exists.id != user_id:
                return False, 'El email ya está registrado por otro usuario.'

        if data['dni'] != user.dni:
            dni_exists = self.dni_exists(data['dni'])
            if dni_exists and dni_exists.id != user_id:
                return False, 'El DNI ya está registrado por otro usuario.'

        # Verificar si hay cambios en los datos
        has_changes = False

        # Verificar campos comunes
        if (data['nombre'] != user.nombre or
            data['apellido'] != user.apellido or
            data['email'] != user.email or
            data['telefono'] != user.telefono or
            data['nacionalidad'] != user.nacionalidad or
            data['dni'] != user.dni):
            has_changes = True

        # Verificar campos específicos de cliente
        if user.tipo == 'cliente':
            if (fecha_nacimiento != user.fecha_nacimiento or
                data['domicilio'] != user.direccion or
                data.get('tarjeta') != user.tarjeta):
                has_changes = True

        # Verificar si hay nueva contraseña
        if data.get('password'):
            has_changes = True
            if len(data['password']) < 8:
                return False, 'La contraseña debe tener al menos 8 caracteres.'
            if data['password'] != data.get('password_confirm'):
                return False, 'Las contraseñas no coinciden.'

        if not has_changes:
            return False, 'No ha realizado ningún cambio'

        # Preparar datos para actualización
        user_dict = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'telefono': data['telefono'],
            'nacionalidad': data['nacionalidad'],
            'dni': data['dni']
        }

        # Agregar campos específicos de cliente si el usuario es cliente
        if user.tipo == 'cliente':
            user_dict.update({
                'fecha_nacimiento': fecha_nacimiento,
                'direccion': data['domicilio'],
                'tarjeta': data.get('tarjeta')
            })

        # Agregar contraseña si se proporcionó
        if data.get('password'):
            user_dict['contrasena'] = data['password']

        try:
            self.user_repository.update_user(user_id, user_dict)
            return True, 'Perfil actualizado exitosamente.'
        except Exception as e:
            return False, f'Error al actualizar el perfil: {str(e)}'

    def register_user(self, data):
        required_fields = ['nombre', 'apellido', 'email', 'password', 'telefono', 'f_nac', 'domicilio', 'nacionalidad', 'dni']
        for field in required_fields:
            if not data.get(field):
                return False, f'El campo {field} es obligatorio.'
        if not is_valid_email(data['email']):
            return False, 'Email inválido.'
        if len(data['password']) < 8:
            return False, 'La contraseña debe tener al menos 8 caracteres.'
        if not is_numeric(data['dni']):
            return False, 'El DNI debe ser numérico.'
        if not is_numeric(data['telefono']):
            return False, 'El teléfono debe ser numérico.'
        if data.get('tarjeta') and not is_numeric(data['tarjeta']):
            return False, 'La tarjeta debe ser numérica.'
        if data['nacionalidad'] not in NACIONALIDADES_VALIDAS:
            return False, 'Nacionalidad inválida.'
        if self.email_exists(data['email']):
            return False, 'El email ya está registrado.'
        if self.dni_exists(data['dni']):
            return False, 'El DNI ya está registrado.'
        fecha_nacimiento = self.parse_fecha_nacimiento(data.get('f_nac'))
        if data.get('f_nac') and not fecha_nacimiento:
            return False, 'Fecha de nacimiento inválida.'
        user_dict = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'contrasena': data['password'],
            'telefono': data['telefono'],
            'fecha_nacimiento': fecha_nacimiento,
            'direccion': data['domicilio'],
            'nacionalidad': data['nacionalidad'],
            'dni': data['dni'],
            'tarjeta': data.get('tarjeta'),
            'tipo': data.get('tipo', 'cliente')
        }
        print(user_dict)
        self.user_repository.create_usuario(user_dict)
        return True, 'Registro exitoso. Ahora puedes iniciar sesión.'

    def authenticate_user(self, email, password):
        user = self.user_repository.get_by_email(email)
        if user and user.contrasena == password:
            return user
        return None 