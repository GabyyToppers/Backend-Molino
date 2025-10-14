from database import usuarios_table

# Limpiamos usuarios anteriores (solo para pruebas)
usuarios_table.truncate()

# Insertamos un usuario real
usuario = {
    "correo": "gabrielapereiradiaz1@gmail.com",  # tu correo real
    "password": "1234",
    "codigo_recuperacion": None,
    "expira_en": None
}

usuarios_table.insert(usuario)
print("✅ Usuario insertado correctamente en la base de datos TinyDB")
