import bcrypt

# La contraseña (b"admin") se pasa como primer argumento de línea de comandos.
# El hash (b"$2b$12$...") se pasa como segundo argumento de línea de comandos.
# Los argumentos de línea de comandos ya deben ser strings, los convertimos a bytes.

# Usamos valores fijos para la demostración, sin usar sys.argv para simplificar
# Si el problema son las comillas, simplificar la entrada es clave.

password = b"admin"
hashed_password = b"$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

result = bcrypt.checkpw(password, hashed_password)
print(result)