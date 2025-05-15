from flask import Blueprint, render_template, request, redirect, url_for

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


# Ruta para crear una nueva propiedad
@main.route('/propiedades/nueva', methods=['GET', 'POST'])
def nueva_propiedad():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nueva_propiedad = Propiedad(
                nombre=request.form['nombre'],
                ubicacion=request.form['ubicacion'],
                precio=float(request.form['precio']),
                cantidad_habitaciones=int(request.form['cantidad_habitaciones']),
                limite_personas=int(request.form['limite_personas']),
                pet_friendly=bool(request.form.get('pet_friendly')),
                cochera=bool(request.form.get('cochera')),
                wifi=bool(request.form.get('wifi')),
                piscina=bool(request.form.get('piscina')),
                patio_trasero=bool(request.form.get('patio_trasero')),
                descripcion=request.form.get('descripcion', '')
            )
            
            # Guardar en la base de datos
            db.session.add(nueva_propiedad)
            db.session.commit()
            
            flash('Propiedad creada exitosamente', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la propiedad: {str(e)}', 'error')
            return render_template('ingresar_nueva_propiedad.html')
    
    return render_template('ingresar_nueva_propiedad.html')
