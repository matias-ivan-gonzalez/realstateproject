import pytest
from flask import Blueprint, render_template_string
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    test_template = '''
    {% extends "base_hero.html" %}
    {% block hero_content %}
      <h2>Contenido de prueba</h2>
    {% endblock %}
    '''
    test_bp = Blueprint('test_bp', __name__)

    @test_bp.route("/test-base-hero")
    def test_base_hero():
        return render_template_string(test_template)

    app.register_blueprint(test_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_base_hero_template_rendering(client):
    response = client.get("/test-base-hero")
    assert response.status_code == 200
    assert b'<main class="hero flex-grow-1 d-flex align-items-center justify-content-center">' in response.data
    assert b'<svg viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice">' in response.data
    assert b'<radialGradient id="grad1"' in response.data
    assert b'<circle cx="400" cy="300" r="300" fill="url(#grad1)" />' in response.data
    assert b'<circle cx="600" cy="150" r="120" fill="var(--bs-primary)" />' in response.data
    assert b'<circle cx="200" cy="450" r="100" fill="var(--bs-secondary)" />' in response.data
    assert b'<stop offset="0%" stop-color="var(--bs-primary)" />' in response.data
    assert b'<stop offset="100%" stop-color="var(--bs-secondary)" />' in response.data
    assert b'class="hero-content container text-center w-100"' in response.data
    assert b'<h2>Contenido de prueba</h2>' in response.data 