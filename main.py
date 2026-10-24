from fastapi import FastAPI, HTTPException
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

class EstadoRenta(BaseModel):
    usuario_id: int
    puede_rentar: bool
    multas_pendientes: int
    motivo: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "usuario_id": 1023456789,
                "puede_rentar": False,
                "multas_pendientes": 2,
                "motivo": "El usuario tiene 2 multa(s) pendiente(s)"
            }
        }

# Simula la columna multas_pendientes de la base de datos (cédula -> cantidad de multas)
MULTAS_PENDIENTES = {
    1012345678: 0,
    1023456789: 2,
    80123456: 0,
    52987654: 0,
    79456123: 0,
}

def _estado_renta(usuario_id: int) -> EstadoRenta:
    if usuario_id not in MULTAS_PENDIENTES:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    multas = MULTAS_PENDIENTES[usuario_id]
    return EstadoRenta(
        usuario_id=usuario_id,
        puede_rentar=multas == 0,
        multas_pendientes=multas,
        motivo=None if multas == 0 else f"El usuario tiene {multas} multa(s) pendiente(s)",
    )

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
    MULTAS_PENDIENTES[usuario.id] = 0
    return {"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email, "rol": usuario.rol}

@app.put("/usuarios/{usuario_id}", response_model=UsuarioResponse, summary="Actualizar usuario", tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, usuario: UsuarioBase):
    """Actualiza la información de un usuario."""
    return {"id": usuario_id, "nombre": usuario.nombre, "email": usuario.email, "rol": usuario.rol}

@app.delete("/usuarios/{usuario_id}", status_code=204, summary="Eliminar un usuario", tags=["Usuarios"])
def eliminar_usuario(usuario_id: int):
    """Elimina un usuario por su ID."""
    return None


# --- MULTAS Y BLOQUEO DE RENTAS ---

@app.get("/usuarios/{usuario_id}/puede-rentar", response_model=EstadoRenta, summary="Consultar si un usuario puede rentar", tags=["Multas"])
def consultar_puede_rentar(usuario_id: int):
    """El servicio de rentas llama este endpoint antes de crear una renta.
    Si `puede_rentar` es false, la renta debe rechazarse."""
    return _estado_renta(usuario_id)

@app.post("/usuarios/{usuario_id}/multas", response_model=EstadoRenta, status_code=201, summary="Registrar una multa", tags=["Multas"])
def registrar_multa(usuario_id: int):
    """Suma una multa al usuario. Desde ese momento no podrá rentar."""
    _estado_renta(usuario_id)  # valida que exista
    MULTAS_PENDIENTES[usuario_id] += 1
    return _estado_renta(usuario_id)

@app.post("/usuarios/{usuario_id}/multas/pagar", response_model=EstadoRenta, summary="Pagar una multa", tags=["Multas"])
def pagar_multa(usuario_id: int):
    """Resta una multa al usuario. Cuando llega a 0, vuelve a poder rentar."""
    _estado_renta(usuario_id)  # valida que exista
    if MULTAS_PENDIENTES[usuario_id] == 0:
        raise HTTPException(status_code=409, detail="El usuario no tiene multas pendientes")
    MULTAS_PENDIENTES[usuario_id] -= 1
    return _estado_renta(usuario_id)
