from flask import Flask, render_template
import os


app = Flask(
    __name__,
    static_folder=os.path.join('..', 'static'),  # Ruta a la carpeta 'static'
    template_folder=os.path.join('..', 'templates')  # Ruta a la carpeta 'templates'
)
# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)