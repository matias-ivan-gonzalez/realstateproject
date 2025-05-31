# run.py
from app import create_app
from routes import main
from database import db
from config import Config


app = create_app()

def execute():
    if __name__ == '__main__':
        app.run(debug=True)

execute()  # Llamada a la función para iniciar la app
