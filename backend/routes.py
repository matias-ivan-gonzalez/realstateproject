from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from architectural_patterns.service.search_service import SearchService

# Crear un Blueprint para las rutas
main = Blueprint('main', __name__)

# Ruta principal
@main.route('/')
def index():
    return render_template('index.html')

# Ruta de login
@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

# Ruta de registro
@main.route('/register', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        # Aquí podrías capturar los datos del formulario si es necesario
        # nombre = request.form.get('nombre')
        # Procesar datos o guardar en la base de datos

        return redirect(url_for('main.login'))  # Redirige al login después del registro

    return render_template('register.html')

@main.route('/search', methods=['GET'])
def search_properties():
    data = {
        'ubicacion' : request.args.get('ubicacion', ''),
        'fecha_inicio' : request.args.get('fecha_inicio', ''),
        'fecha_fin' : request.args.get('fecha_fin', ''),
        'precio_min' : request.args.get('precio_min', ''),
        'precio_max': request.args.get('precio_max', ''),
        'caracteristicas': request.args.getlist('caracteristicas'),
        'pagina': int(request.args.get('pagina', 1)),
        'por_pagina': 4,
        'orden_precio': request.args.get('orden_precio', '')
    }
    search_service = SearchService()
    resultado = search_service.search_properties(data)

    if resultado['success'] == True:
        return render_template(
            'search_results.html',
            propiedades=resultado['propiedades'],
            pagina=resultado['pagina'],
            por_pagina=resultado['por_pagina'],
            total_paginas=resultado['total_paginas'],
            total_propiedades=resultado['total_propiedades'],
            ubicacion=data['ubicacion'],
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            precio_min=data['precio_min'],
            precio_max=data['precio_max'],
            caracteristicas=data['caracteristicas'],
            cantidad_noches=resultado['cantidad_noches'],
            precios_totales=resultado['precios_totales'],
            mensaje=resultado['mensaje'],
            hide_navbar_search_btn=True,
            orden_precio=data['orden_precio']
        )
    else:
        # Si hay error, resultado es una tupla (False, mensaje)
        mensaje = resultado['mensaje']
        if mensaje == "No se encontraron propiedades disponibles en esta ubicación, pruebe otra ubicación.":
            flash(mensaje, 'danger')    
            return redirect(url_for('main.index'))     
        else:
           flash(mensaje, 'danger')
           return render_template(
            'search_results.html',
            propiedades=[],
            pagina=data['pagina'],
            por_pagina=data['por_pagina'],
            total_paginas=0,
            total_propiedades=0,
            ubicacion=data['ubicacion'],
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            precio_min=data['precio_min'],
            precio_max=data['precio_max'],
            caracteristicas=data['caracteristicas'],
            cantidad_noches=None,
            precios_totales={},
            mensaje=mensaje,
            hide_navbar_search_btn=True,
            orden_precio=data['orden_precio']
        )
           


# Ruta para mostrar el formulario de nueva propiedad
@main.route('/propiedades/nueva', methods=['GET', 'POST'])
def nueva_propiedad():
    return render_template('nueva_propiedad.html')

# Ruta para mostrar el formulario de modificar propiedad
@main.route('/propiedades/modificar', methods=['GET', 'POST'])
def modificar_propiedad():
    # Diccionario de ejemplo con datos de una propiedad
    propiedad = {
        "nombre": "Casa de Prueba",
        "ubicacion": "Calle Falsa 123",
        "precio": 150000,
        "cantidad_habitaciones": 3,
        "limite_personas": 5,
        "pet_friendly": True,
        "cochera": False,
        "wifi": True,
        "piscina": False,
        "patio_trasero": True,
        "descripcion": "Una casa de prueba para modificar."
    }
    action_url = "/propiedades/modificar"
    return render_template('modificar_propiedad.html', propiedad=propiedad, action_url=action_url)