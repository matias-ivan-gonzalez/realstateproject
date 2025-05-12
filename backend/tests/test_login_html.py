def test_login_template_rendering(client):
    """
    Testea que el template login.html se renderiza correctamente y cumple con las especificaciones visuales y funcionales.
    """
    response = client.get('/login')
    assert response.status_code == 200

    # Verifica que el título en el bloque <title> es correcto
    assert b'<title>Iniciar sesión - Alquilando</title>' in response.data

    # Verifica que el fondo SVG está presente (proviene de base_hero.html)
    assert b'<svg viewBox="0 0 800 600"' in response.data
    assert b'<circle cx="400" cy="300" r="300"' in response.data

    # Verifica la estructura del contenedor principal (card)
    assert b'<div class="card p-4 shadow text-start"' in response.data
    assert b'<h2 class="text-center text-secondary mb-4">¡Hola, de nuevo!</h2>' in response.data

    # Verifica el formulario y sus campos
    assert b'<form method="post">' in response.data
    assert b'<label for="email" class="form-label text-secondary">Email</label>' in response.data
    assert b'<input type="email" class="form-control" id="email" name="email"' in response.data
    assert b'<label for="password" class="form-label text-secondary">Contraseña</label>' in response.data
    assert b'<input type="password" class="form-control" id="password" name="password"' in response.data

    # Verifica el botón y el enlace
    assert b'<button type="submit" class="btn btn-primary">Iniciar sesión</button>' in response.data
    assert b'<a href="/recuperar" class="text-decoration-none text-secondary small">Recuperar contraseña</a>' in response.data

    # Verifica que sigue habiendo atributos de accesibilidad
    assert b'id="email"' in response.data and b'name="email"' in response.data
    assert b'id="password"' in response.data and b'name="password"' in response.data
