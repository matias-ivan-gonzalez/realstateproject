def test_footer_rendering(client):
    """
    Testea que el template footer.html se renderiza correctamente en las páginas que lo incluyen.
    """
    response = client.get('/')
    assert response.status_code == 200

    # Verifica que el contenedor del footer está presente
    assert b'<footer' in response.data
    assert b'class="bg-secondary text-center text-white py-3"' in response.data

    # Verifica que el correo de contacto está presente y es un enlace
    assert b'Contacto:' in response.data
    assert b'href="mailto:alquilando@gmail.com"' in response.data
    assert b'class="link-light"' in response.data

    # Verifica que la dirección está presente
    assert b'Direccion: Calle Falsa 123, Ciudad Ficticia' in response.data
