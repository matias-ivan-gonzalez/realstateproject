from unittest.mock import patch

def test_nueva_propiedad_template_rendering(client):
    response = client.get('/propiedades/nueva')
    assert response.status_code == 200

    # Verifica el título en el bloque <title>
    assert b'<title>Nueva Propiedad - Alquilando</title>' in response.data

    # Verifica el encabezado principal
    assert b'<h2 class="text-center text-secondary mb-3">Ingresar Nueva Propiedad</h2>' in response.data

    # Verifica los campos principales del formulario
    assert b'<input type="text" class="form-control" id="nombre" name="nombre" required>' in response.data
    assert b'<input type="text" class="form-control" id="ubicacion" name="ubicacion" required>' in response.data
    assert b'<input type="number" class="form-control" id="precio" name="precio" step="0.01" required>' in response.data
    assert b'<input type="number" class="form-control" id="cantidad_habitaciones" name="cantidad_habitaciones" min="1" required>' in response.data
    assert b'<input type="number" class="form-control" id="limite_personas" name="limite_personas" min="1" required>' in response.data

    # Verifica los checkboxes de características
    assert b'<input type="checkbox" class="form-check-input" id="pet_friendly" name="pet_friendly">' in response.data
    assert b'<input type="checkbox" class="form-check-input" id="cochera" name="cochera">' in response.data
    assert b'<input type="checkbox" class="form-check-input" id="wifi" name="wifi">' in response.data
    assert b'<input type="checkbox" class="form-check-input" id="piscina" name="piscina">' in response.data
    assert b'<input type="checkbox" class="form-check-input" id="patio_trasero" name="patio_trasero">' in response.data

    # Verifica el textarea de descripción
    assert b'<textarea class="form-control" id="descripcion" name="descripcion" rows="2" placeholder="Descripci\xc3\xb3n de la propiedad...">' in response.data

    # Verifica los botones
    assert b'<button type="submit" class="btn btn-primary">Guardar Propiedad</button>' in response.data
    assert b'<a href="/" class="btn btn-secondary">Cancelar</a>' in response.data

def test_modificar_propiedad_template_rendering(client):
    response = client.get('/propiedades/modificar')
    assert response.status_code == 200

    # Verifica el título en el bloque <title>
    assert b'<title>Modificar Propiedad - Alquilando</title>' in response.data

    # Verifica el encabezado principal
    assert b'<h2 class="text-center text-secondary mb-3">Modificar Propiedad</h2>' in response.data

    # Verifica los campos principales del formulario con los valores de ejemplo
    assert b'value="Casa de Prueba"' in response.data
    assert b'value="Calle Falsa 123"' in response.data
    assert b'value="150000"' in response.data
    assert b'value="3"' in response.data
    assert b'value="5"' in response.data

    # Verifica los checkboxes (pet_friendly, wifi y patio_trasero deben estar checked)
    assert b'id="pet_friendly" name="pet_friendly" checked' in response.data
    assert b'id="wifi" name="wifi" checked' in response.data
    assert b'id="patio_trasero" name="patio_trasero" checked' in response.data
    # cochera y piscina no deben estar checked
    assert b'id="cochera" name="cochera"' in response.data
    assert b'id="piscina" name="piscina"' in response.data

    # Verifica el textarea de descripción
    assert b'Una casa de prueba para modificar.' in response.data

    # Verifica el botón principal
    assert b'<button type="submit" class="btn btn-primary">Guardar Cambios</button>' in response.data
