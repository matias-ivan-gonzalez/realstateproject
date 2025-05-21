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

     # Verifica que el título en el bloque <title> es correcto
     assert '<title>Crear cuenta - Alquilando</title>'.encode('utf-8') in response.data

     # Verifica que el fondo SVG está presente (proviene de base_hero.html)
     assert b'<svg viewBox="0 0 800 600"' in response.data
     assert b'<circle cx="400" cy="300" r="300"' in response.data

     # Verifica la estructura del contenedor principal (card)
     assert b'<div class="card p-4 shadow text-start"' in response.data
     assert b'<h2 class="text-center text-secondary mb-4">Crea tu cuenta</h2>' in response.data

     # Verifica campos del formulario
     campos = [
         ("nombre", "Nombre"),
         ("apellido", "Apellido"),
         ("email", "Email"),
         ("password", "Contraseña"),
         ("telefono", "Teléfono"),
         ("f_nac", "Fecha de nacimiento"),
         ("domicilio", "Domicilio"),
         ("nacionalidad", "Nacionalidad"),
         ("dni", "DNI"),
         ("tarjeta", "Tarjeta"),
     ]

     for field_id, label in campos:
         # Verifica etiqueta y atributos básicos
         if field_id == 'tarjeta':
             # Tarjeta debe indicarse como opcional
             assert f'<label for="{field_id}" class="form-label text-secondary">{label}'.encode('utf-8') in response.data
             assert b'(opcional)' in response.data, "Falta indicación de campo opcional para tarjeta"
             # No debe tener atributo required
             assert f'<input type="text" class="form-control" id="{field_id}" name="{field_id}"'.encode('utf-8') in response.data
             assert b'name="tarjeta" required' not in response.data, "El campo tarjeta no debe ser obligatorio"
         else:
             etiqueta = f'<label for="{field_id}" class="form-label text-secondary">{label}</label>'
             assert etiqueta.encode('utf-8') in response.data, f"Falta etiqueta para {field_id}"
             assert f'id="{field_id}"'.encode('utf-8') in response.data, f"Falta atributo id para {field_id}"
             assert f'name="{field_id}"'.encode('utf-8') in response.data, f"Falta atributo name para {field_id}"

     # Verifica el botón de envío
     assert b'<button type="submit" class="btn btn-primary">Confirmar</button>' in response.data
