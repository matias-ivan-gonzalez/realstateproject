import pytest

def test_ingresar_nueva_propiedad_template_rendering(client):
    """
    Testea que el template ingresar_nueva_propiedad.html se renderiza correctamente y cumple con las especificaciones visuales y funcionales.
    """
    rutas = ['/propiedades/nueva', '/propiedades/nueva/']
    response = None
    for ruta in rutas:
        response = client.get(ruta)
        if response.status_code == 200:
            break
    else:
        pytest.fail(f"Ninguna ruta válida encontrada. Se intentaron: {rutas}")

    assert response.status_code == 200

    # Verifica el título en el bloque <title>
    assert b'<title>Nueva Propiedad - Alquilando</title>' in response.data

    # Verifica el encabezado del formulario
    assert b'<h2 class="text-center text-secondary mb-3">Ingresar Nueva Propiedad</h2>' in response.data

    # Verifica los campos del formulario
    campos = [
        ("nombre", "Nombre de la Propiedad"),
        ("ubicacion", "Ubicación"),
        ("precio", "Precio"),
        ("cantidad_habitaciones", "Cantidad de Habitaciones"),
        ("limite_personas", "Límite de Personas"),
        ("pet_friendly", "Pet Friendly"),
        ("cochera", "Cochera"),
        ("wifi", "WiFi"),
        ("piscina", "Piscina"),
        ("patio_trasero", "Patio Trasero"),
        ("descripcion", "Descripción"),
    ]

    for field_id, label in campos:
        if field_id in ['pet_friendly', 'cochera', 'wifi', 'piscina', 'patio_trasero']:
            # Son checkboxes
            assert f'<input type="checkbox" class="form-check-input" id="{field_id}" name="{field_id}"'.encode('utf-8') in response.data
            assert f'<label class="form-check-label text-secondary" for="{field_id}">{label}</label>'.encode('utf-8') in response.data
        elif field_id == 'descripcion':
            assert f'<textarea class="form-control" id="{field_id}" name="{field_id}"'.encode('utf-8') in response.data
            assert f'<label for="{field_id}" class="form-label text-secondary">{label}</label>'.encode('utf-8') in response.data
        else:
            assert f'<input type="text" class="form-control" id="{field_id}" name="{field_id}"'.encode('utf-8') in response.data or \
                   f'<input type="number" class="form-control" id="{field_id}" name="{field_id}"'.encode('utf-8') in response.data
            assert f'<label for="{field_id}" class="form-label text-secondary">{label}'.encode('utf-8') in response.data

    # Verifica el botón de envío
    assert b'<button type="submit" class="btn btn-primary">Guardar Propiedad</button>' in response.data
    # Verifica el botón de cancelar
    assert b'<a href="' in response.data and b'class="btn btn-secondary">Cancelar</a>' in response.data