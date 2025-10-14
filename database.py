from tinydb import TinyDB, where

# Base de datos principal
db = TinyDB('database.json')

# Tablas (colecciones)
empleados_table = db.table('empleados')
contratos_table = db.table('contratos')
usuarios_table = db.table('usuarios')

