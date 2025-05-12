# Test para la ruta '/'
def test_index(client):
    # Realiza una solicitud GET a la ruta '/'
    response = client.get('/')
    
    # Verifica que la respuesta tenga el código de estado 200
    assert response.status_code == 200

# Test para la ruta '/login'
def test_login(client):
    # Realiza una solicitud GET a la ruta '/login'
    response = client.get('/login')
    
    # Verifica que la respuesta tenga el código de estado 200
    assert response.status_code == 200

    # Realiza una solicitud POST a la ruta '/login'
    response_post = client.post('/login', data={})
    
    # Verifica que la respuesta tenga el código de estado 200
    assert response_post.status_code == 200


# Test para la ruta '/register' (GET)
def test_register_get(client):
    # Realiza una solicitud GET a la ruta '/register'
    response = client.get('/register')
    
    # Verifica que la respuesta tenga el código de estado 200
    assert response.status_code == 200

# Test para la ruta '/register' (POST)
def test_register_post(client):
    # Realiza una solicitud POST a la ruta '/register' con datos vacíos
    response = client.post('/register', data={}, follow_redirects=False)
    
    # Verifica que redirija (302) al login tras el POST
    assert response.status_code == 302
    # Comprueba que la cabecera 'Location' apunte a '/login'
    assert response.headers['Location'].endswith('/login')
