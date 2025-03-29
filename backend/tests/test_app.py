# Test para la ruta principal
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data  # Asegúrate de que se renderiza HTML

# Test para una ruta inexistente
def test_404(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404
