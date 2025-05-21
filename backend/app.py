from flask import Flask
import os
from routes import main  # Asegúrate de importar el Blueprint correctamente
from database import db  # Importa tu configuración de base de datos desde un archivo separado
from config import Config  # Importa la gitclase Config
from werkzeug.security import generate_password_hash
from datetime import date

flask_params = {
    'static_folder': os.path.join('..', 'static'),
    'template_folder': os.path.join('..', 'templates')
}

def create_app():
    app = Flask(__name__, **flask_params)

    # Cargar configuración desde config.py
    app.config.from_object(Config)
    app.secret_key = 'mi_clave_super_secreta_123'  # Clave secreta para sesión y mensajes flash
    

    # Inicializar SQLAlchemy
    db.init_app(app)
    
    with app.app_context():
        from models.rol import Rol
        from models.permiso import Permiso
        from models.user import Cliente, Administrador, Encargado, SuperUsuario
        from models.propiedad import Propiedad
        from models.imagen import Imagen
        from models.propiedad_administrador import propiedad_administrador
        from models.favoritos import favoritos
        # Crear tablas
        db.create_all()

        # Inicializar la base de datos con datos de ejemplo
        from init_db import init_db
        init_db()
        

    # Registrar el Blueprint
    app.register_blueprint(main)

    return app
