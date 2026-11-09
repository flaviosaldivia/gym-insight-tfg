from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal

class SocioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_socio: int
    nombre: str
    apellido: str
    email: str
    telefono: str | None
    fecha_alta: date
    estado: str

class MembresiaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_membresia: int
    id_socio: int
    plan: str
    fecha_inicio: date
    fecha_vencimiento: date
    estado: str
    importe: Decimal
