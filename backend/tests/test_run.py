import pytest
import requests
from run import app  # Importamos la app desde run.py
import threading
import time
from werkzeug.serving import make_server

# Función auxiliar para correr la app en un hilo y poder detenerla después
def run_app_in_thread(app, host='127.0.0.1', port=5000):
    server = make_server(host, port, app)
    server.serve_forever()

# Test para verificar que la app se levanta en el puerto 5000 y responde correctamente
def test_run_py():
    # Iniciamos la app en un hilo para no bloquear el test
    server_thread = threading.Thread(target=run_app_in_thread, args=(app,))
    server_thread.daemon = True  # Permite que el hilo se cierre cuando el programa principal termine
    server_thread.start()
    
    # Damos un poco de tiempo para que el servidor se inicie (esperamos que arranque)
    time.sleep(2)
    
    try:
        # Verificar que la app esté corriendo en el puerto 5000
        response = requests.get('http://127.0.0.1:5000')  # Realizamos una solicitud GET a la app
        
        # Verifica que la respuesta sea correcta (código de estado 200)
        assert response.status_code == 200
        
        # Verifica que el contenido principal esté presente en la respuesta
        assert b'Frontend levantado desde Flask' in response.content
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f'Error al hacer ping a la app: {e}')  # Si ocurre algún error en la solicitud, falla el test
    
    # Finalizamos el hilo del servidor después de la verificación
    # No es necesario hacer join() aquí ya que estamos utilizando daemon threads
