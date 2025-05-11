def test_index_template_rendering(client):
    """
    Testea que el template index.html se renderiza correctamente y es robusto.
    """
    response = client.get('/')
    assert response.status_code == 200

    # Verifica que el bloque <main> está presente con las clases adecuadas
    assert b'<main class="hero flex-grow-1 d-flex align-items-center justify-content-center">' in response.data

    # Verifica que el SVG de fondo está presente y tiene los atributos correctos
    assert b'<svg viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice">' in response.data
    assert b'<radialGradient id="grad1"' in response.data
    assert b'<circle cx="400" cy="300" r="300" fill="url(#grad1)" />' in response.data
    assert b'<circle cx="600" cy="150" r="120" fill="var(--bs-primary)" />' in response.data
    assert b'<circle cx="200" cy="450" r="100" fill="var(--bs-secondary)" />' in response.data

    # Verifica que los colores del gradiente radial son los esperados
    assert b'<stop offset="0%" stop-color="var(--bs-primary)" />' in response.data
    assert b'<stop offset="100%" stop-color="var(--bs-secondary)" />' in response.data

    # Verifica que el texto principal está presente con las clases correctas
    assert b'<h1 class="display-5 text-secondary">Alquilando, cada estadia una experiencia unica</h1>' in response.data

    # Verifica que el título en el bloque <head> es el correcto
    assert b'<title>Alquilando</title>' in response.data

    # Validaciones de accesibilidad (atributos y estructura)
    # Verifica que el SVG tiene el atributo `preserveAspectRatio`
    assert b'preserveAspectRatio="xMidYMid slice"' in response.data

    # Comprueba que todos los colores del SVG están definidos con variables CSS
    assert b'fill="var(--bs-primary)"' in response.data
    assert b'fill="var(--bs-secondary)"' in response.data

    # Validaciones adicionales del contenedor de contenido
    assert b'class="hero-content container text-center w-100"' in response.data
