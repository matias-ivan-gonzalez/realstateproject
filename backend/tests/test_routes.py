# Test para la ruta '/'
def test_index(client):
    # Realiza una solicitud GET a la ruta '/'
    response = client.get('/')
    #
    # Verifica que la respuesta tenga el código de estado 200
    assert response.status_code == 200
    
    # Verifica que el texto principal esté presente
    assert b'Frontend levantado desde Flaskaaaaa' in response.data
    
    # Verifica que los archivos estáticos estén incluidos (por ejemplo, Bootstrap CSS)
    assert b'href="/static/css/bootstrap.min.css"' in response.data
    assert b'src="/static/js/bootstrap.bundle.min.js"' in response.data
