from .routes.encargado import encargado

def create_app():
    app.register_blueprint(encargado) 