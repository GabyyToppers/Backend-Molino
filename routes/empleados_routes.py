from flask import Blueprint, request, jsonify
from tinydb import Query
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import empleados_table

empleados = Blueprint('empleados', __name__)

# Obtener todos los empleados
@empleados.route('/empleados', methods=['GET'])
def get_empleados():
    return jsonify(empleados_table.all()), 200


# Obtener un empleado por ID (doc_id de TinyDB)
@empleados.route('/empleados/<int:id>', methods=['GET'])
def get_empleado(id):
    empleado = empleados_table.get(doc_id=id)
    if empleado:
        empleado['id'] = id
        return jsonify(empleado), 200
    return jsonify({"error": "Empleado no encontrado"}), 404


# Crear un nuevo empleado
@empleados.route('/empleados', methods=['POST'])
def add_empleado():
    data = request.get_json()
    required_fields = ['NRO_DOCUMENTO', 'NOMBRE', 'APELLIDO', 'EDAD', 'GENERO', 'CARGO', 'CORREO', 'NRO_CONTACTO', 'ESTADO']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    empleados_table.insert(data)
    return jsonify({"message": "Empleado agregado correctamente"}), 201


# Actualizar un empleado existente
@empleados.route('/empleados/<int:id>', methods=['PUT'])
def update_empleado(id):
    data = request.get_json()
    empleado = empleados_table.get(doc_id=id)
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    empleados_table.update(data, doc_ids=[id])
    return jsonify({"message": "Empleado actualizado"}), 200


# Eliminar un empleado
@empleados.route('/empleados/<int:id>', methods=['DELETE'])
def delete_empleado(id):
    empleado = empleados_table.get(doc_id=id)
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    empleados_table.remove(doc_ids=[id])
    return jsonify({"message": "Empleado eliminado"}), 200
