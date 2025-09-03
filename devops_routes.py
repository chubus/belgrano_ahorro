from flask import Blueprint, current_app

# Blueprint de DevOps con prefijo /devops
devops_bp = Blueprint('devops_bp', __name__, url_prefix='/devops')


@devops_bp.route('/agregar_sucursal', methods=['POST'])
def devops_agregar_sucursal():
    """Proxy para alta de sucursales desde panel DevOps.
    Reutiliza la lógica existente de app.py (agregar_sucursal_mejorado).
    """
    handler = current_app.view_functions.get('agregar_sucursal_mejorado')
    if handler:
        return handler()
    return ("Handler agregar_sucursal_mejorado no disponible", 500)



