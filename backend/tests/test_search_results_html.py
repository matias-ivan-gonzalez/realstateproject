import pytest
from flask import Flask, render_template_string, request


# Simulate a minimal Flask app for template rendering
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

# Example template string (should be replaced with the actual template in real tests)
TEMPLATE = """
{% extends "base_hero.html" %}
{% block hero_content %}
<form method="get">
    <input type="search" name="ubicacion" id="ubicacion" value="{{ ubicacion }}">
    <input type="date" id="fecha_inicio" name="fecha_inicio" value="{{ fecha_inicio or '' }}">
    <input type="date" id="fecha_fin" name="fecha_fin" value="{{ fecha_fin or '' }}">
    <input type="number" id="precio_min" name="precio_min" value="{{ precio_min or '' }}">
    <input type="number" id="precio_max" name="precio_max" value="{{ precio_max or '' }}">
    <select id="orden_precio" name="orden_precio">
        <option value="" {% if not orden_precio %}selected{% endif %}>---</option>
        <option value="asc" {% if orden_precio == 'asc' %}selected{% endif %}>Precio - Menor a Mayor</option>
        <option value="desc" {% if orden_precio == 'desc' %}selected{% endif %}>Precio - Mayor a Menor</option>
    </select>
    <input type="checkbox" name="caracteristicas" value="wifi" id="wifi" {% if 'wifi' in caracteristicas %}checked{% endif %}>
    <input type="checkbox" name="caracteristicas" value="pileta" id="pileta" {% if 'pileta' in caracteristicas %}checked{% endif %}>
    <input type="checkbox" name="caracteristicas" value="cochera" id="cochera" {% if 'cochera' in caracteristicas %}checked{% endif %}>
    <input type="checkbox" name="caracteristicas" value="mascotas" id="mascotas" {% if 'mascotas' in caracteristicas %}checked{% endif %}>
    <input type="checkbox" name="caracteristicas" value="patio" id="patio" {% if 'patio' in caracteristicas %}checked{% endif %}>
    <button type="submit">Buscar</button>
</form>
{% if propiedades %}
    {% for propiedad in propiedades %}
        <div class="card">
            <h5>{{ propiedad.nombre }}</h5>
            <p>{{ propiedad.ubicacion }}</p>
            {% if cantidad_noches %}
                <p>${{ propiedad.precio }}</p>
                <p>${{ precios_totales[propiedad.id] }}</p>
            {% endif %}
            <p>{{ propiedad.limite_personas }}</p>
            {% if propiedad.latitud and propiedad.longitud %}
                <div id="mapa-{{ propiedad.id }}"></div>
            {% endif %}
        </div>
    {% endfor %}
{% endif %}
{% endblock %}
"""

@pytest.mark.parametrize("form_data,expected", [
    ({"ubicacion": "Córdoba"}, "value=\"Córdoba\""),
    ({"fecha_inicio": "2024-06-01"}, "value=\"2024-06-01\""),
    ({"fecha_fin": "2024-06-10"}, "value=\"2024-06-10\""),
    ({"precio_min": "1000"}, "value=\"1000\""),
    ({"precio_max": "5000"}, "value=\"5000\""),
    ({"orden_precio": "asc"}, "selected>Precio - Menor a Mayor"),
    ({"orden_precio": "desc"}, "selected>Precio - Mayor a Menor"),
    ({"caracteristicas": ["wifi", "pileta"]}, "id=\"wifi\" checked"),
])
def test_search_form_fields(app, form_data, expected):
    with app.app_context():
        html = render_template_string(
            TEMPLATE,
            ubicacion=form_data.get("ubicacion", ""),
            fecha_inicio=form_data.get("fecha_inicio", ""),
            fecha_fin=form_data.get("fecha_fin", ""),
            precio_min=form_data.get("precio_min", ""),
            precio_max=form_data.get("precio_max", ""),
            orden_precio=form_data.get("orden_precio", ""),
            caracteristicas=form_data.get("caracteristicas", []),
            propiedades=None
        )
        assert expected in html

def test_propiedades_rendering(app):
    propiedades = [
        {
            "id": 1,
            "nombre": "Casa en el Lago",
            "ubicacion": "Bariloche",
            "precio": 2000,
            "limite_personas": 6,
            "latitud": -41.1335,
            "longitud": -71.3103,
            "wifi": True,
            "piscina": False,
            "cochera": True,
            "pet_friendly": True,
            "patio_trasero": False,
        }
    ]
    precios_totales = {1: 6000}
    with app.app_context():
        html = render_template_string(
            TEMPLATE,
            propiedades=propiedades,
            cantidad_noches=3,
            precios_totales=precios_totales,
            caracteristicas=[],
            ubicacion="",
            fecha_inicio="",
            fecha_fin="",
            precio_min="",
            precio_max="",
            orden_precio="",
        )
        assert "Casa en el Lago" in html
        assert "Bariloche" in html
        assert "$2000" in html
        assert "$6000" in html
        assert "mapa-1" in html

def test_checkbox_checked_for_caracteristicas(app):
    with app.app_context():
        html = render_template_string(
            TEMPLATE,
            caracteristicas=["wifi", "cochera"],
            propiedades=None,
            ubicacion="",
            fecha_inicio="",
            fecha_fin="",
            precio_min="",
            precio_max="",
            orden_precio="",
        )
        assert 'id="wifi" checked' in html
        assert 'id="cochera" checked' in html
        assert 'id="pileta" checked' not in html

def test_no_propiedades_message(app):
    with app.app_context():
        html = render_template_string(
            TEMPLATE,
            propiedades=None,
            caracteristicas=[],
            ubicacion="",
            fecha_inicio="",
            fecha_fin="",
            precio_min="",
            precio_max="",
            orden_precio="",
        )
        # Should not render any card if no propiedades
        assert "card" not in html