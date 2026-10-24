"""Acceso a la base de datos PostgreSQL del microservicio de usuarios."""
import os
from typing import Optional

import psycopg2


def _url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://usuarios_user:usuarios_pass@localhost:5432/usuarios_db",
    )


def cambiar_estado(usuario_id: int, activo: bool) -> bool:
    """Actualiza la columna `activo` del usuario (la cédula es el id).
    Devuelve True si el usuario existía, False si no se encontró.
    Es idempotente: repetir el mismo evento deja el mismo resultado."""
    conexion = psycopg2.connect(_url())
    try:
        with conexion, conexion.cursor() as cur:  # `with conexion` hace commit
            cur.execute(
                "UPDATE usuarios SET activo = %s WHERE id = %s",
                (activo, usuario_id),
            )
            return cur.rowcount > 0
    finally:
        conexion.close()


def obtener_activo(usuario_id: int) -> Optional[bool]:
    """Devuelve el valor de `activo`, o None si el usuario no existe."""
    conexion = psycopg2.connect(_url())
    try:
        with conexion, conexion.cursor() as cur:
            cur.execute("SELECT activo FROM usuarios WHERE id = %s", (usuario_id,))
            fila = cur.fetchone()
            return fila[0] if fila else None
    finally:
        conexion.close()
