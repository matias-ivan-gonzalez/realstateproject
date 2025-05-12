def test_login_template_rendering(client):
    """
    Testea que el template login.html se renderiza correctamente y cumple con las especificaciones.
    """
    response = client.get('/login')
    assert response.status_code == 200

    # Verifica que el título en el bloque <title> es correcto
    assert '<title>Iniciar sesión - Alquilando</title>'.encode("utf-8") in response.data

    # Verifica que el <main> está presente con las clases esperadas
    assert '<main class="d-flex flex-column align-items-center justify-content-center flex-grow-1 py-5 bg-light">'.encode("utf-8") in response.data

    # Verifica la estructura del contenedor principal (card)
    assert '<div class="card p-4 shadow" style="max-width: 400px; width: 100%; z-index: 2;">'.encode("utf-8") in response.data

    # Verifica el encabezado
    assert '<h2 class="text-center text-secondary mb-4">¡Hola, de nuevo!</h2>'.encode("utf-8") in response.data

    # Verifica que el formulario tiene el método POST
    assert '<form method="post">'.encode("utf-8") in response.data

    # Verifica el campo de email
    assert '<label for="email" class="form-label text-secondary">Email</label>'.encode("utf-8") in response.data
    assert '<input type="email" class="form-control" id="email" name="email" placeholder="ejemplo@correo.com" required>'.encode("utf-8") in response.data

    # Verifica el campo de contraseña
    assert '<label for="password" class="form-label text-secondary">Contraseña</label>'.encode("utf-8") in response.data
    assert '<input type="password" class="form-control" id="password" name="password" placeholder="********" required>'.encode("utf-8") in response.data

    # Verifica el botón de envío
    assert '<button type="submit" class="btn btn-primary">Iniciar sesión</button>'.encode("utf-8") in response.data

    # Verifica el enlace de "Recuperar contraseña"
    assert '<a href="/recuperar" class="text-decoration-none text-secondary small">Recuperar contraseña</a>'.encode("utf-8") in response.data

    # Validaciones de accesibilidad
    # Verifica que todos los campos del formulario tienen atributos `id` y `name` únicos
    assert 'id="email"'.encode("utf-8") in response.data
    assert 'name="email"'.encode("utf-8") in response.data
    assert 'id="password"'.encode("utf-8") in response.data
    assert 'name="password"'.encode("utf-8") in response.data

    # Verifica que el botón tiene una clase accesible
    assert 'class="btn btn-primary"'.encode("utf-8") in response.data
