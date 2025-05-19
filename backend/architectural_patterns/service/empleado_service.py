from architectural_patterns.repository.empleado_repository import EmpleadoRepository
from models.rol import Rol
from flask import session

class EmpleadoService:
    def __init__(self, repository=None):
        self.repository = repository or EmpleadoRepository()

    def crear_empleado(self, data):
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
            return False, "La contraseña debe tener al menos 6 caracteres."

        # Validación de unicidad del DNI
        if self.repository.get_by_dni(data["dni"]):
            return False, "Ya existe un usuario con ese DNI."

        # Validación de unicidad del email
        if self.repository.get_by_email(data["email"]):
            return False, "Ya existe un usuario con ese email."

        # Validar permisos según el rol del usuario actual
        user_rol = session.get('rol')
        if user_rol == 'superusuario':
            roles_permitidos = ['Administrador', 'Encargado']
        else:
            roles_permitidos = ['Encargado']
            
        if data["rol"] not in roles_permitidos:
            return False, "No tienes permiso para crear un empleado con ese rol"

        # Obtener el rol
        rol_nombre = data["rol"].lower()  # Convertir a minúsculas para coincidir con la BD
        if rol_nombre == "administrador":
            rol_nombre = "admin"  # El rol en la BD es 'admin', no 'administrador'
        rol_db = Rol.query.filter_by(nombre=rol_nombre).first()
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
            "tipo": "administrador" if rol_nombre == "admin" else "encargado"
        }

        try:
            self.repository.create_empleado(empleado_data)
            return True, "Empleado registrado exitosamente."
        except Exception as e:
            return False, f"Error al registrar el empleado: {str(e)}" 