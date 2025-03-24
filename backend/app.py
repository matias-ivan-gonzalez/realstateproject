from flask import Flask
import os
from routes import main  # Asegúrate de importar el Blueprint correctamente

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join('..', 'static'),
        template_folder=os.path.join('..', 'templates')
    )
    # Registrar el Blueprint
    app.register_blueprint(main)
    return app