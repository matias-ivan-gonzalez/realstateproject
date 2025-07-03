import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MERCADOPAGO_ACCESS_TOKEN = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "TEST-8693493935674671-062521-fd192291bb110416f4cdba99dc715151-632376171")  # Reemplaza por tu access token de test
MERCADOPAGO_PUBLIC_KEY = os.environ.get("MERCADOPAGO_PUBLIC_KEY", "TEST-92eba423-9be3-4689-b2b5-01f0244272e7")  # Reemplaza por tu public key de test

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'mydatabase.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secretkey'