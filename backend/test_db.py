import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect(
            user="reservas",
            password="reservas",
            database="reservasdb",
            host="127.0.0.1",
            port=5432
        )
        print("✅ Conexión exitosa")
        await conn.close()
    except Exception as e:
        print("❌ Error:", e)

asyncio.run(test())

import bcrypt

password = "admin"
hash_str = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

# Verificar
match = bcrypt.checkpw(password.encode('utf-8'), hash_str.encode('utf-8'))
print("¿Coincide?", match)

# usamos tu wrapper exacto
import bcrypt as bcrypt_native

class pwd_context:
    @staticmethod
    def hash(password: str) -> str:
        return bcrypt_native.hashpw(
            password.encode('utf-8')[:72],
            bcrypt_native.gensalt()
        ).decode('utf-8')

hash_admin = pwd_context.hash("admin")
print("Hash nuevo para 'admin':", hash_admin)


import bcrypt as bcrypt_native

password = "admin"
hash_actual = "$2b$12$2vxEp0lONUcpzYeXxhk9juTU/tSsL3w3Zbmd6n8Yhh3Sib/VG1GPa"

# ✅ exactamente como lo haces en tu endpoint
match = bcrypt_native.checkpw(
    password.encode('utf-8')[:72],
    hash_actual.encode('utf-8')
)

print("¿Coincide con tu wrapper?", match)