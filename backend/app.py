from flask import Flask
import os
from routes import main  # Asegúrate de importar el Blueprint correctamente
from database import db  # Importa tu configuración de base de datos desde un archivo separado
from config import Config  # Importa la clase Config




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
        from models import Rol, Permiso, User, Rol_Permiso
        db.create_all()


    # Registrar el Blueprint
    app.register_blueprint(main)

    return app
