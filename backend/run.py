# run.py
from app import create_app, socketio
from routes import main
from database import db
from config import Config


app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
