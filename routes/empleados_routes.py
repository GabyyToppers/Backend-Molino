from flask import Blueprint, request, jsonify
from tinydb import Query
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import empleados_table

empleados = Blueprint('empleados', __name__)
Empleado = Query()

# Obtener todos los empleados
@empleados.route('/empleados', methods=['GET'])
def get_empleados():
    return jsonify(empleados_table.all()), 200


# Obtener un empleado por NRO_DOCUMENTO
@empleados.route('/empleados/<string:nro_documento>', methods=['GET'])
def get_empleado(nro_documento):
    empleado = empleados_table.get(Empleado.NRO_DOCUMENTO == nro_documento)
    if empleado:
        return jsonify(empleado), 200
    return jsonify({"error": "Empleado no encontrado"}), 404


# Crear un nuevo empleado
@empleados.route('/empleados', methods=['POST'])
def add_empleado():
    data = request.get_json()
    required_fields = ['NRO_DOCUMENTO', 'NOMBRE', 'APELLIDO', 'EDAD', 'GENERO', 'CARGO', 'CORREO', 'NRO_CONTACTO', 'ESTADO']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Verificar si ya existe un empleado con ese número de documento
    if empleados_table.get(Empleado.NRO_DOCUMENTO == data['NRO_DOCUMENTO']):
        return jsonify({"error": "Ya existe un empleado con ese número de documento"}), 400

    empleados_table.insert(data)
    return jsonify({"message": "Empleado agregado correctamente"}), 201


# Actualizar un empleado existente por NRO_DOCUMENTO
@empleados.route('/empleados/<string:nro_documento>', methods=['PUT'])
def update_empleado(nro_documento):
    data = request.get_json()
    empleado = empleados_table.get(Empleado.NRO_DOCUMENTO == nro_documento)
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404

    empleados_table.update(data, Empleado.NRO_DOCUMENTO == nro_documento)
    return jsonify({"message": "Empleado actualizado"}), 200


# Eliminar un empleado por NRO_DOCUMENTO
@empleados.route('/empleados/<string:nro_documento>', methods=['DELETE'])
def delete_empleado(nro_documento):
    empleado = empleados_table.get(Empleado.NRO_DOCUMENTO == nro_documento)
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404

    empleados_table.remove(Empleado.NRO_DOCUMENTO == nro_documento)
    return jsonify({"message": "Empleado eliminado"}), 200
