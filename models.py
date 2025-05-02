import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional

# Modelo de Producto
class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category: int
    brand: int
    name_short: str
    name: str
    colors: list[str]
    storages: list[int]
    images: list[str]
    tags: list[str]

# Modelo de Precio
class Price(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    id_product: UUID
    status: int
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

class Reviews(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    stars: float
    comment: str
    image: str

class Category(BaseModel):
    id: Optional[int] = None
    category: str