import pytest

def test_render_agregar_empleado_html(client):
    response = client.get('/empleados/nuevo')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    # Verifica que los campos principales estén presentes
    assert '<h2 class="text-center text-secondary mb-4">Agregar nuevo empleado</h2>' in html
    assert 'name="nombre"' in html
    assert 'name="apellido"' in html
    assert 'name="dni"' in html
    assert 'name="telefono"' in html
    assert 'name="nacionalidad"' in html
    assert 'name="email"' in html
    assert 'name="contrasena"' in html
    assert 'name="rol"' in html
    # Verifica que el botón de guardar esté presente
    assert 'type="submit"' in html 