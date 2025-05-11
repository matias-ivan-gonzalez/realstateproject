import re

def test_navbar_template_rendering(client):
    """
    Testea que el template del navbar se renderiza correctamente y cumple con las especificaciones,
    incluyendo el comportamiento en pantallas grandes y pequeñas.
    """
    # Test para pantallas grandes (Desktop)
    response_desktop = client.get('/')
    assert response_desktop.status_code == 200

    # Verifica que la etiqueta <nav> está presente con las clases correctas
    assert '<nav class="navbar navbar-expand-lg navbar-dark bg-secondary">'.encode("utf-8") in response_desktop.data

    # Verifica el contenedor principal dentro del navbar
    assert '<div class="container">'.encode("utf-8") in response_desktop.data

    # Verifica el logo con imagen
    assert '<a class="navbar-brand d-flex align-items-center" href="/">'.encode("utf-8") in response_desktop.data
    assert '<img src="/static/img/logo_alquiloando.png" alt="Logo" width="30" height="30" class="me-2">'.encode("utf-8") in response_desktop.data
    assert 'Alquilando'.encode("utf-8") in response_desktop.data

    # Verifica el formulario de búsqueda
    assert '<form class="d-flex ms-auto me-3" action="/search" method="get">'.encode("utf-8") in response_desktop.data
    assert '<input class="form-control me-2" type="search" name="ubicacion" placeholder="Ubicación" aria-label="Ubicación">'.encode("utf-8") in response_desktop.data
    assert '<button class="btn btn-outline-light" type="submit">Buscar</button>'.encode("utf-8") in response_desktop.data

    # Verifica los enlaces de navegación
    assert '<ul class="navbar-nav mb-2 mb-lg-0">'.encode("utf-8") in response_desktop.data
    assert '<li class="nav-item me-2">'.encode("utf-8") in response_desktop.data
    assert '<a class="btn btn-outline-light" href="/login">Iniciar sesión</a>'.encode("utf-8") in response_desktop.data
    assert '<a class="btn btn-outline-light" href="/register">Registrarse</a>'.encode("utf-8") in response_desktop.data

    # Verifica el contenedor colapsable (esto debería estar presente siempre)
    assert '<div class="collapse navbar-collapse" id="navContent">'.encode("utf-8") in response_desktop.data

    # Verifica los atributos ARIA para accesibilidad
    assert 'aria-controls="navContent"'.encode("utf-8") in response_desktop.data
    assert 'aria-expanded="false"'.encode("utf-8") in response_desktop.data
    assert 'aria-label="Toggle navigation"'.encode("utf-8") in response_desktop.data
    assert 'aria-label="Ubicación"'.encode("utf-8") in response_desktop.data

    # Test para pantallas pequeñas (Mobile)
    response_mobile = client.get('/', environ_base={'REMOTE_ADDR': '192.168.1.1'})  # Simula un dispositivo móvil
    assert response_mobile.status_code == 200

    # Verifica que el navbar esté colapsado inicialmente en pantallas pequeñas
    assert b'collapse navbar-collapse' in response_mobile.data

    # Verifica que el navbar no se muestra expandido
    assert b'aria-expanded="false"' in response_mobile.data

    # Verifica que el campo de búsqueda tiene atributos ARIA
    assert 'aria-label="Ubicación"'.encode("utf-8") in response_mobile.data

    # Verifica que los enlaces de navegación están presentes en el navbar
    assert '<a class="btn btn-outline-light" href="/login">Iniciar sesión</a>'.encode("utf-8") in response_mobile.data
    assert '<a class="btn btn-outline-light" href="/register">Registrarse</a>'.encode("utf-8") in response_mobile.data
