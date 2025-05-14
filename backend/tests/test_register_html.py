import re
import pytest

def test_crear_cuenta_template_rendering(client):
    """
    Testea que el template de crear cuenta se renderiza correctamente y cumple con las especificaciones visuales y funcionales.
    """
    # Probamos varias posibles rutas donde podría estar el endpoint
    rutas = ['/crear-cuenta', '/crear-cuenta/', '/register', '/register/']
    response = None
    for ruta in rutas:
        response = client.get(ruta)
        if response.status_code == 200:
            break
    else:
        pytest.fail(f"Ninguna ruta válida encontrada. Se intentaron: {rutas}")

    assert response.status_code == 200

    # Título
    assert b'<title>Crear cuenta - Alquilando</title>' in response.data

    # Fondo SVG
    assert b'<svg viewBox="0 0 800 600"' in response.data
    assert b'<circle cx="400" cy="300" r="300"' in response.data

    # Contenedor principal
    assert b'<div class="card p-4 shadow text-start"' in response.data
    assert b'<h2 class="text-center text-secondary mb-4">Crea tu cuenta</h2>' in response.data

    # Campos obligatorios: etiqueta, id, name y required
    campos_obligatorios = [
        ("nombre", "Nombre"),
        ("apellido", "Apellido"),
        ("email", "Email"),
        ("password", "Contraseña"),
        ("telefono", "Teléfono"),
        ("f_nac", "Fecha de nacimiento"),
        ("domicilio", "Domicilio"),
        ("nacionalidad", "Nacionalidad"),
        ("dni", "DNI"),
    ]
    for field_id, label in campos_obligatorios:
        # label
        etiqueta = f'<label for="{field_id}" class="form-label text-secondary">{label}</label>'
        assert etiqueta.encode() in response.data, f"Falta etiqueta para {field_id}"
        # input completo (aunque en varias líneas)
        m = re.search(
            rb'<input\b[^>]*\bid="' + field_id.encode() + rb'"[^>]*>', 
            response.data, 
            flags=re.DOTALL
        )
        assert m, f"No se encontró el <input> de {field_id}"
        assert b'name="' + field_id.encode() + b'"' in m.group(0), f"Falta name en {field_id}"
        assert b'required' in m.group(0), f"El campo {field_id} debe seguir siendo obligatorio"

    # Campo "tarjeta": label genérico + "(opcional)", id/name y SIN required
    # 1) label existe y contiene "(opcional)"
    assert re.search(rb'<label\b[^>]*for="tarjeta"[^>]*>.*\(opcional\).*?</label>',
                     response.data, flags=re.DOTALL), "Falta label de tarjeta con '(opcional)'"
    # 2) input opcional
    m_tarjeta = re.search(
        rb'<input\b[^>]*\bid="tarjeta"[^>]*>', 
        response.data, 
        flags=re.DOTALL
    )
    assert m_tarjeta, "No se encontró el <input> de tarjeta"
    assert b'name="tarjeta"' in m_tarjeta.group(0), "Falta name en tarjeta"
    assert b'required' not in m_tarjeta.group(0), "El input de tarjeta no debe tener 'required'"

    # Botón de envío
    assert b'<button type="submit" class="btn btn-primary">Confirmar</button>' in response.data
