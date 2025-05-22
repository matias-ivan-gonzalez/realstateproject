from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from ..models.propiedad import Propiedad
from .. import db
from architectural_patterns.controller.empleado_controller import EmpleadoController

encargado = Blueprint('encargado', __name__)

@encargado.route('/mis-propiedades')
@login_required
def mis_propiedades():
    empleado_controller = EmpleadoController()
    return empleado_controller.list_my_propiedades(request, current_user)
    