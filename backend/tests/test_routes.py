from unittest.mock import patch

# Test para la ruta '/'
def test_index(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/')
        assert response.status_code == 200

# Test para la ruta '/login'
def test_login(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/login')
        assert response.status_code == 200

        response_post = client.post('/login', data={})
        assert response_post.status_code == 200

# Test para la ruta '/register' (GET)
def test_register_get(client):
    with patch('flask.render_template', return_value=''):
        response = client.get('/register')
        assert response.status_code == 200

# Test para la ruta '/register' (POST)
def test_register_post(client):
    with patch('flask.render_template', return_value=''):
        response = client.post('/register', data={})
        assert response.status_code in (200, 302)

def test_register_post_success(client):
    # Datos válidos para registro exitoso
    data = {
        'nombre': 'Ana',
        'apellido': 'Lopez',
        'email': 'test_registro_exitoso@mail.com',
        'password': '12345678',
        'telefono': '456123',
        'f_nac': '2000-01-01',
        'domicilio': 'Otra',
        'nacionalidad': 'Argentina',
        'dni': '99999999',
        'tarjeta': '1234'
    }
    response = client.post('/register', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_get_nueva_propiedad(client):
    response = client.get('/propiedades/nueva')
    assert response.status_code == 200

def test_get_modificar_propiedad(client):
    response = client.get('/propiedades/modificar')
    assert response.status_code == 200