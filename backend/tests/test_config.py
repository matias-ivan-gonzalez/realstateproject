import os
import pytest
from config import Config, BASE_DIR

def test_config_sqlalchemy_uri():
    expected_uri = f"sqlite:///{os.path.join(BASE_DIR, 'mydatabase.db')}"
    assert Config.SQLALCHEMY_DATABASE_URI == expected_uri, "SQLALCHEMY_DATABASE_URI no es correcto"

def test_config_sqlalchemy_track_modifications():
    assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False, "SQLALCHEMY_TRACK_MODIFICATIONS debería ser False"
