# backend/app/main.py
# 1.  Cargar .env ANTES que cualquier otro import
from dotenv import load_dotenv
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, locales, reservations, admin

load_dotenv()

# 3.  Crear la app
app = FastAPI(title="Reserva Locales API", version="1.0.0")

# 4.  CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5.  Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(locales.router, prefix="/api/locales", tags=["locales"])
app.include_router(reservations.router, prefix="/api/reservations", tags=["reservations"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# 6.  Health check
@app.get("/")
def read_root():
    return {"msg": "API de Reserva de Locales"}