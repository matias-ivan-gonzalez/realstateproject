from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

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
def search():
    from models.propiedad import Propiedad
    ubicacion = request.args.get('ubicacion', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    precio_min = request.args.get('precio_min', '')
    precio_max = request.args.get('precio_max', '')
    caracteristicas = request.args.getlist('caracteristicas')
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 5

    # Filtrar propiedades por ubicación (búsqueda simple)
    propiedades = []
    if ubicacion:
        propiedades = Propiedad.query.filter(Propiedad.ubicacion.ilike(f"%{ubicacion}%")).all()
    else:
        propiedades = Propiedad.query.all()

    # Calcular cantidad de noches y precio total
    precios_totales = {}
    cantidad_noches = None
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            cantidad_noches = (fecha_fin_dt - fecha_inicio_dt).days
            if cantidad_noches < 1:
                cantidad_noches = 1
        except Exception:
            cantidad_noches = None
    
    propiedades_filtradas = []
    for propiedad in propiedades:
        # Filtro por características
        cumple_caracteristicas = True
        for c in caracteristicas:
            if c == 'wifi' and not propiedad.wifi:
                cumple_caracteristicas = False
            if c == 'pileta' and not propiedad.piscina:
                cumple_caracteristicas = False
            if c == 'cochera' and not propiedad.cochera:
                cumple_caracteristicas = False
            if c == 'mascotas' and not propiedad.pet_friendly:
                cumple_caracteristicas = False
            if c == 'patio' and not propiedad.patio_trasero:
                cumple_caracteristicas = False
        if not cumple_caracteristicas:
            continue
        if cantidad_noches:
            precio_total = round(propiedad.precio * cantidad_noches, 2)
            precios_totales[propiedad.id] = precio_total
            # Filtrar por precio mínimo y máximo si están presentes
            cumple_min = True
            cumple_max = True
            if precio_min:
                try:
                    cumple_min = precio_total >= float(precio_min)
                except Exception:
                    cumple_min = True
            if precio_max:
                try:
                    cumple_max = precio_total <= float(precio_max)
                except Exception:
                    cumple_max = True
            if cumple_min and cumple_max:
                propiedades_filtradas.append(propiedad)
        else:
            precios_totales[propiedad.id] = None
            # Si no hay fechas, no filtrar por precio total
            propiedades_filtradas.append(propiedad)

    total_propiedades = len(propiedades_filtradas)
    total_paginas = (total_propiedades + por_pagina - 1) // por_pagina
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    propiedades_pagina = propiedades_filtradas[inicio:fin]

    # Mensaje específico para rango de precios
    if precio_min and precio_max and total_propiedades == 0:
        flash("No se encontraron propiedades dentro del rango de precios seleccionado. Intente ajustar el rango de precios.", "warning")
    elif total_propiedades == 0:
        flash("No se encontraron propiedades disponibles en esta ubicación, pruebe otra ubicación.", "warning")

    return render_template('search_results.html', propiedades=propiedades_pagina, ubicacion=ubicacion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, precio_min=precio_min, precio_max=precio_max, precios_totales=precios_totales, cantidad_noches=cantidad_noches, caracteristicas=caracteristicas, pagina=pagina, total_paginas=total_paginas)

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