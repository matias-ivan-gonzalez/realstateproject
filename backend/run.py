# run.py
from app import create_app
from routes import main
from database import db
from config import Config
import atexit
import os

app = create_app()

DB_PATH = os.path.join(os.path.dirname(__file__), 'mydatabase.db')

def borrar_bd():
    try:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
    except Exception as e:
        print(f"Error cerrando la base de datos: {e}")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Base de datos eliminada al cerrar el servidor.")
        except Exception as e:
            print(f"No se pudo eliminar la base de datos: {e}")

atexit.register(borrar_bd)

def execute():
    if __name__ == '__main__':
        app.run(debug=True)

execute()  # Llamada a la función para iniciar la app
