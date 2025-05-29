from architectural_patterns.repository.empleado_repository import EmpleadoRepository
from models.rol import Rol
from flask import session
from sqlalchemy.exc import IntegrityError

class EmpleadoService:
    def __init__(self, repository=None):
        self.repository = repository or EmpleadoRepository()

    def crear_empleado(self, data):
        # Mapeo de nombres visibles a nombres de la base de datos
        MAPEO_ROLES = {
            "Administrador": "admin",
            "Encargado": "encargado"
        }
        # Validación de campos obligatorios
        required_fields = [
            "nombre", "apellido", "dni", "telefono", "nacionalidad", 
            "email", "contrasena", "rol"
        ]
        for field in required_fields:
            if not data.get(field):
                return False, f"El campo {field} es obligatorio."

        # Validación de contraseña
        if len(data["contrasena"]) < 6:
            return False, "Registro fallido. La contraseña debe tener 6 caracteres como minimo"

        # Validación de unicidad del DNI y nacionalidad
        if self.repository.get_by_dni_and_nacionalidad(data["dni"], data["nacionalidad"]):
            return False, "Registro fallido. El documento ya está registrado para esa nacionalidad"

        # Validación de unicidad del email
        if self.repository.get_by_email(data["email"]):
            return False, "Registro fallido. El mail ingresado ya se encuentra registrado"

        # Validar permisos según el rol del usuario actual
        user_rol = session.get('rol')
        if user_rol == 'superusuario':
            roles_permitidos = ['Administrador', 'Encargado']
        else:
            roles_permitidos = ['Encargado']
        
        rol_nombre_form = data["rol"]
        if rol_nombre_form not in roles_permitidos:
            return False, "No tienes permiso para crear un empleado con ese rol"

        # Mapear al nombre de la base de datos
        rol_nombre_db = MAPEO_ROLES.get(rol_nombre_form)

        rol_db = Rol.query.filter_by(nombre=rol_nombre_db).first()
        if not rol_db:
            return False, "El rol especificado no existe."

        # Preparar datos para crear el usuario
        empleado_data = {
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "dni": data["dni"],
            "telefono": data["telefono"],
            "nacionalidad": data["nacionalidad"],
            "email": data["email"],
            "contrasena": data["contrasena"],
            "rol": rol_db,
            "tipo": "administrador" if rol_nombre_db == "admin" else "encargado"
        }

        try:
            self.repository.create_empleado(empleado_data)
            return True, "Registro exitoso"
        except IntegrityError:
            return False, "Registro fallido. El documento ya está registrado para esa nacionalidad"
        except Exception as e:
            return False, f"Error al registrar el empleado: {str(e)}" 