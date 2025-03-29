from flask import Flask
import os
from routes import main  # Asegúrate de importar el Blueprint correctamente

flask_params = {
    'static_folder': os.path.join('..', 'static'),         
    'template_folder': os.path.join('..', 'templates')
}

def create_app():
    app = Flask(__name__, **flask_params)

    # Registrar el Blueprint
    app.register_blueprint(main)
    return app