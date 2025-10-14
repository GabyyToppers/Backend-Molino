from flask import Blueprint, request, jsonify
from tinydb import Query
from database import contratos_table, empleados_table
from services.report_service import generar_pdf, generar_excel

contratos = Blueprint('contratos', __name__)

# Obtener todos los contratos
@contratos.route('/contratos', methods=['GET'])
def get_contratos():
    return jsonify(contratos_table.all()), 200

# Crear contrato (debe tener relación con un empleado)
@contratos.route('/contratos', methods=['POST'])
def add_contrato():
    data = request.get_json()
    required_fields = ['fecha_inicio', 'fecha_fin', 'valor_contrato', 'empleado']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Validamos que el empleado exista
    Empleado = Query()
    empleado = empleados_table.get(Empleado.NOMBRE == data['empleado'])
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404

    contratos_table.insert(data)
    return jsonify({"message": "Contrato agregado correctamente"}), 201

# Actualizar contrato
@contratos.route('/contratos/<int:id>', methods=['PUT'])
def update_contrato(id):
    data = request.get_json()
    contrato = contratos_table.get(doc_id=id)
    if not contrato:
        return jsonify({"error": "Contrato no encontrado"}), 404
    contratos_table.update(data, doc_ids=[id])
    return jsonify({"message": "Contrato actualizado"}), 200

# Eliminar contrato
@contratos.route('/contratos/<int:id>', methods=['DELETE'])
def delete_contrato(id):
    contrato = contratos_table.get(doc_id=id)
    if not contrato:
        return jsonify({"error": "Contrato no encontrado"}), 404
    contratos_table.remove(doc_ids=[id])
    return jsonify({"message": "Contrato eliminado"}), 200

# Buscar contratos por nombre o documento del empleado
@contratos.route('/buscar', methods=['GET'])
def buscar_contratos():
    query = request.args.get('q', '')
    Empleado = Query()
    empleado = empleados_table.get((Empleado.NOMBRE == query) | (Empleado.NRO_DOCUMENTO == query))

    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404

    Contrato = Query()
    contratos_encontrados = contratos_table.search(Contrato.empleado == empleado['NOMBRE'])
    return jsonify({
        "empleado": empleado,
        "contratos": contratos_encontrados,
        "total_contratos": len(contratos_encontrados)
    }), 200

# Descargar PDF
@contratos.route('/reporte/pdf', methods=['GET'])
def reporte_pdf():
    empleado_nombre = request.args.get('empleado')
    Contrato = Query()
    contratos_empleado = contratos_table.search(Contrato.empleado == empleado_nombre)
    file_path = generar_pdf(empleado_nombre, contratos_empleado)
    return jsonify({"message": f"Reporte PDF generado: {file_path}"}), 200

# Descargar Excel
@contratos.route('/reporte/excel', methods=['GET'])
def reporte_excel():
    empleado_nombre = request.args.get('empleado')
    Contrato = Query()
    contratos_empleado = contratos_table.search(Contrato.empleado == empleado_nombre)
    file_path = generar_excel(empleado_nombre, contratos_empleado)
    return jsonify({"message": f"Reporte Excel generado: {file_path}"}), 200
