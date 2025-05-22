from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from ..models.propiedad import Propiedad
from .. import db

encargado = Blueprint('encargado', __name__)

@encargado.route('/mis-propiedades')
@login_required
def mis_propiedades():
    # Verificar que el usuario es un encargado
    if not hasattr(current_user, 'propiedades_encargadas'):
        return "Acceso no autorizado", 403
    
    # Obtener el número de página de la URL, por defecto 1
    page = request.args.get('page', 1, type=int)
    # Obtener el filtro de ubicación
    ubicacion = request.args.get('ubicacion', '')
    
    # Consulta base
    query = Propiedad.query.filter_by(encargado_id=current_user.id)
    
    # Aplicar filtro de ubicación si existe
    if ubicacion:
        query = query.filter(Propiedad.ubicacion.ilike(f'%{ubicacion}%'))
    
    # Paginar los resultados
    propiedades = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('encargado/mis_propiedades.html', propiedades=propiedades) 