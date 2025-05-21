def test_index_template_rendering(client):
    """
    Testea que el template index.html se renderiza correctamente con base_hero.html.
    """
    response = client.get('/')
    assert response.status_code == 200

    # Verifica que el título en el bloque <head> es el correcto
    assert b'<title>Alquilando</title>' in response.data

    # Verifica que el <main> y el SVG de fondo están presentes (vienen de base_hero.html)
    assert b'<main class="hero flex-grow-1 d-flex align-items-center justify-content-center">' in response.data
    assert b'<svg viewBox="0 0 800 600" preserveAspectRatio="xMidYMid slice">' in response.data
    assert b'<radialGradient id="grad1"' in response.data
    assert b'<circle cx="400" cy="300" r="300" fill="url(#grad1)" />' in response.data
    assert b'<circle cx="600" cy="150" r="120" fill="var(--bs-primary)" />' in response.data
    assert b'<circle cx="200" cy="450" r="100" fill="var(--bs-secondary)" />' in response.data
    assert b'<stop offset="0%" stop-color="var(--bs-primary)" />' in response.data
    assert b'<stop offset="100%" stop-color="var(--bs-secondary)" />' in response.data

    # Verifica que el contenido específico del index se renderiza en el bloque hero_content
    assert b'<h1 class="display-5 text-secondary">Alquilando, cada estad\xc3\xada una experiencia \xc3\xbanica</h1>' in response.data

    # Verifica que el contenedor esté presente
    assert b'class="hero-content container text-center w-100"' in response.data
