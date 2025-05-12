def test_base_template_rendering(client):
    """
    Testea el template base.html al acceder a una ruta que lo utilice.
    """
    response = client.get('/')
    assert response.status_code == 200

    # Verifica que el título principal se renderiza correctamente
    assert b'<title>Alquilando</title>' in response.data

    # Verifica que los estilos CSS están presentes
    assert b'href="/static/css/bootstrap.min.css"' in response.data
    assert b'href="/static/customCss/styles.css"' in response.data

    # Verifica que los scripts de JavaScript están presentes
    assert b'src="/static/js/bootstrap.bundle.min.js"' in response.data

    # Verifica que las inclusiones importantes están presentes
    assert b'navbar' in response.data.lower()  # Asegura que incluye el navbar
    assert b'footer' in response.data.lower()  # Asegura que incluye el footer
