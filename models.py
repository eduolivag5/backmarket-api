import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional

# Modelo de Producto
class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    marca: int
    modelo: str
    color: list[str]
    almacenamiento: list[int]
    fecha_lanzamiento: datetime.date
    images: list[str]

# Modelo de Precio
class Price(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    id_product: UUID
    status: int
    battery: int
    price: float

class Brand(BaseModel):
    id: Optional[int] = None
    marca: str

class PhoneStatus(BaseModel):
    id: Optional[int] = None
    estado: str
    descripcion: str

class BatteryStatus(BaseModel):
    id: Optional[int] = None
    estado: str
    descripcion: str

class Colors(BaseModel):
    id: Optional[int] = None
    color: str