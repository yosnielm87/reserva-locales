#!/usr/bin/env python3
import os
import sys
import requests
from typing import Optional

# ---------- CONFIG ----------
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/auth/login"
LIST_ENDPOINT = "/api/admin/reservations"
EMAIL = "admin@admin.com"
PASSWORD = "123456"
# ----------------------------

session = requests.Session()

def login() -> str:
    """Devuelve el access_token o aborta."""
    url = BASE_URL + LOGIN_ENDPOINT
    payload = {"email": EMAIL, "password": PASSWORD}
    r = session.post(url, json=payload)
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        sys.exit("Login ok pero sin access_token")
    return token

def first_reservation_id(token: str) -> str:
    """Devuelve el primer UUID de reserva."""
    url = BASE_URL + LIST_ENDPOINT
    r = session.get(url, headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    data = r.json()
    if not data:
        sys.exit("No hay reservas en BD")
    return data[0]["id"]

def patch_status(token: str, uid: str, new_status: str = "approved") -> None:
    url = f"{BASE_URL}/api/admin/reservations/{uid}/status"
    r = session.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=new_status,  # envía el string directamente
    )
    r.raise_for_status()
    print(f"✅ Reserva {uid} → '{new_status}' (HTTP {r.status_code})")

def main() -> None:
    try:
        token = login()
        uid = first_reservation_id(token)
        patch_status(token, uid)
    except requests.HTTPError as e:
        print("❌ HTTPError:", e.response.status_code, e.response.text)

if __name__ == "__main__":
    main()