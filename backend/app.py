from flask import Flask
import os
from routes import main  # Asegúrate de importar el Blueprint correctamente
from database import db  # Importa tu configuración de base de datos desde un archivo separado
from config import Config  # Importa la gitclase Config
from werkzeug.security import generate_password_hash
from datetime import date
from flask_mail import Mail

# Obtener la ruta absoluta del directorio actual
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

flask_params = {
    'static_folder': os.path.join(BASE_DIR, '..', 'static'),
    'template_folder': os.path.join(BASE_DIR, '..', 'templates')
}

mail = Mail()  # Instancia global

def create_app():
    app = Flask(__name__, **flask_params)
    app.secret_key = "superclaveultrasecreta_2024_!@#random"

    # Cargar configuración desde config.py
    app.config.from_object(Config)
    app.secret_key = 'mi_clave_super_secreta_123'  # Clave secreta para sesión y mensajes flash
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'alquilandopropiedades@gmail.com'
    app.config['MAIL_PASSWORD'] = 'kvbisebwjatkdnrw'
    mail.init_app(app)

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
        from models.reserva import Reserva
        # Crear tablas
        db.create_all()

        # Inicializar la base de datos con datos de ejemplo
        from init_db import init_db
        init_db()
        

    # Registrar el Blueprint
    app.register_blueprint(main)

    return app
