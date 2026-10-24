from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(
    title="Microservicio de Usuarios",
    description="API para la gestión e identificación de usuarios",
    version="1.0.0"
)

# Modelo de datos para las respuestas y peticiones (Contrato Swagger)
class UsuarioBase(BaseModel):
    nombre: str
    email: str
    rol: Optional[str] = "cliente"

class UsuarioCreate(UsuarioBase):
    # El id es el número de cédula: lo envía el cliente, no se autogenera
    id: int = Field(..., ge=1, le=9999999999, description="Número de cédula del usuario")
    password: str

class UsuarioResponse(UsuarioBase):
    id: int = Field(..., description="Número de cédula del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1012345678,
                "nombre": "Juan Pérez",
                "email": "juan@example.com",
                "rol": "cliente"
            }
        }

# --- ENDPOINTS (Solo exponen el contrato/Swagger, no requieren DB) ---

@app.get("/usuarios", response_model=List[UsuarioResponse], summary="Obtener lista de usuarios", tags=["Usuarios"])
def obtener_usuarios():
    """Retorna la lista de usuarios registrados."""
    return [
        {"id": 1012345678, "nombre": "Juan Pérez", "email": "juan@example.com", "rol": "cliente"}
    ]

@app.get("/usuarios/{usuario_id}", response_model=UsuarioResponse, summary="Obtener un usuario por cédula", tags=["Usuarios"])
def obtener_usuario(usuario_id: int):
    """Retorna los detalles de un usuario según su número de cédula."""
    return {"id": usuario_id, "nombre": "Juan Pérez", "email": "juan@example.com", "rol": "cliente"}

@app.post("/usuarios", response_model=UsuarioResponse, status_code=201, summary="Crear un nuevo usuario", tags=["Usuarios"])
def crear_usuario(usuario: UsuarioCreate):
    """Crea un nuevo usuario. El id corresponde al número de cédula."""
    return {"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email, "rol": usuario.rol}

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse, summary="Actualizar usuario", tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, usuario: UsuarioBase):
    """Actualiza la información de un usuario."""
    return {"id": usuario_id, "nombre": usuario.nombre, "email": usuario.email, "rol": usuario.rol}

@app.delete("/usuarios/{usuario_id}", status_code=204, summary="Eliminar un usuario", tags=["Usuarios"])
def eliminar_usuario(usuario_id: int):
    """Elimina un usuario por su ID."""
    return None