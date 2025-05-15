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
        response = client.post('/register', data={}, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/login')


def test_get_nueva_propiedad(client):
    response = client.get('/propiedades/nueva')
    assert response.status_code == 200