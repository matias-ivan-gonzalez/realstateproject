from architectural_patterns.repository.user_repository import UserRepository
from models.user import Administrador, Encargado
from database import db

class EmpleadoRepository(UserRepository):
    def get_administradores(self):
        """Obtiene todos los administradores"""
        return Administrador.query.all()
    
    def get_encargados(self):
        """Obtiene todos los encargados"""
        return Encargado.query.all()
    
    def get_empleado_by_id(self, id):
        """Obtiene un empleado por su ID"""
        return Administrador.query.get(id) or Encargado.query.get(id)
    
    def create_empleado(self, empleado_data):
        """Crea un nuevo empleado según su tipo"""
        if empleado_data["tipo"] == "administrador":
            nuevo_empleado = Administrador(**empleado_data)
        elif empleado_data["tipo"] == "encargado":
            nuevo_empleado = Encargado(**empleado_data)
        else:
            raise ValueError("Tipo de empleado no válido")
            
        db.session.add(nuevo_empleado)
        db.session.commit()
        return nuevo_empleado
    
    def get_by_dni_and_nacionalidad(self, dni, nacionalidad):
        return Administrador.query.filter_by(dni=dni, nacionalidad=nacionalidad).first() or Encargado.query.filter_by(dni=dni, nacionalidad=nacionalidad).first() 