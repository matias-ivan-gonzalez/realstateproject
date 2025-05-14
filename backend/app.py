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

    # Inicializar SQLAlchemy
    db.init_app(app)
    
    with app.app_context():
        from models.Rol import Rol
        from models.Permiso import Permiso
        from models.User import Cliente, Administrador, Encargado, SuperUsuario
        from models.Propiedad import Propiedad
        from models.Imagen import Imagen
        from models.Propiedad_Administrador import propiedad_administrador
        from models.Favoritos import favoritos
        # Crear tablas
        db.create_all()

        # Inicializar la base de datos con datos de ejemplo
        from init_db import init_db
        init_db()
        

    # Registrar el Blueprint
    app.register_blueprint(main)

    return app
