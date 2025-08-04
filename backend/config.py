import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MERCADOPAGO_ACCESS_TOKEN = os.environ.get("")  # Reemplaza por tu access token de test
MERCADOPAGO_PUBLIC_KEY = os.environ.get("")  # Reemplaza por tu public key de test

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'mydatabase.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secretkey'