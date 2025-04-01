import datetime
import os
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from uuid import UUID, uuid4
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Conectar a PostgreSQL
conn = psycopg2.connect(
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    dbname=DBNAME
)
cursor = conn.cursor()

# Crear aplicación FastAPI
app = FastAPI(
    title="API de Productos y Precios BackMarket",
    description="Esta API permite gestionar productos y precios en una base de datos PostgreSQL.",
    version="1.0.0",
    contact={
        "name": "Eduardo Oliva Garcia",
        "email": "eduolivag5@gmail.com",
    },
)

# Configuración de CORS para permitir cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Modelo de datos para productos
class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    marca: int
    modelo: str
    color: int
    almacenamiento: int
    fecha_lanzamiento: datetime.date
    images: list[str]

# Modelo de datos para precios
class Price(BaseModel):
    id: str
    id_product: int
    status: int
    battery: int
    precio: float

# Obtener todos los productos
@app.get("/products")
def get_products():
    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return {"error": False, "message": "OK", "data": [
            {
                "id": p[0], "created_at": p[1], "marca": p[2], "modelo": p[3],
                "color": p[4], "almacenamiento": p[5], "fecha_lanzamiento": p[6], "images": p[7]
            } for p in products
        ]}
    except Exception as e:
        return {"error": True, "message": str(e), "data": []}

# Obtener un producto por ID
@app.get("/products/details")
def get_product_by_id(id: UUID = Query(..., alias="id")):
    try:
        cursor.execute("SELECT * FROM products WHERE id = %s", (str(id),))
        product = cursor.fetchone()
        if product:
            return {"error": False, "message": "OK", "data": {
                "id": product[0], "created_at": product[1], "marca": product[2],
                "modelo": product[3], "color": product[4], "almacenamiento": product[5],
                "fecha_lanzamiento": product[6], "images": product[7]
            }}
        else:
            return {"error": True, "message": "Producto no encontrado", "data": None}
    except Exception as e:
        return {"error": True, "message": str(e), "data": None}

# Obtener todos los precios
@app.get("/prices")
def get_prices():
    try:
        cursor.execute("SELECT * FROM prices")
        prices = cursor.fetchall()
        return {"error": False, "message": "OK", "data": [
            {"id": p[0], "id_product": p[1], "status": p[2], "battery": p[3], "price": p[4]}
            for p in prices
        ]}
    except Exception as e:
        return {"error": True, "message": str(e), "data": []}

# Obtener precio por ID de producto
@app.get("/prices/details")
def get_price_by_product(id: UUID = Query(..., alias="id")):
    try:
        cursor.execute("SELECT * FROM prices WHERE id_product = %s", (str(id),))
        price = cursor.fetchall()
        if price:
            return {"error": False, "message": "OK", "data": [
                {"id": p[0], "id_product": p[1], "status": p[2], "battery": p[3], "price": p[4]}
                for p in price
            ]}
        else:
            return {"error": True, "message": "Precio no encontrado para este producto", "data": None}
    except Exception as e:
        return {"error": True, "message": str(e), "data": None}

# Crear un producto
@app.post("/products", summary="Crear un producto", description="Crea un nuevo producto en la base de datos.")
def create_product(product: Product):
    try:
        query = """
            INSERT INTO products (marca, modelo, color, almacenamiento, fecha_lanzamiento, image_urls) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (product.marca, product.modelo, product.color, product.almacenamiento, product.fecha_lanzamiento, product.images)
        cursor.execute(query, values)
        conn.commit()
        return {"error": False, "message": "Producto creado correctamente", "data": product}
    except Exception as e:
        conn.rollback()
        return {"error": True, "message": "Error al crear producto: " + str(e), "data": None}

# Actualizar un producto por ID
@app.put("/products")
def update_product(id: UUID = Query(..., alias="id"), product: Product = None):
    try:
        query = """
            UPDATE products 
            SET marca = %s, modelo = %s, color = %s, almacenamiento = %s, fecha_lanzamiento = %s, image_urls = %s
            WHERE id = %s
        """
        values = (product.marca, product.modelo, product.color, product.almacenamiento, product.fecha_lanzamiento, product.images, str(id))
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": True, "message": "Producto no encontrado", "data": None}
        return {"error": False, "message": "Producto actualizado correctamente", "data": None}
    except Exception as e:
        conn.rollback()
        return {"error": True, "message": str(e), "data": None}

# Eliminar un producto por ID
@app.delete("/products")
def delete_product(id: UUID = Query(..., alias="id")):
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (str(id),))
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": True, "message": "Producto no encontrado", "data": None}
        return {"error": False, "message": "Producto eliminado correctamente", "data": None}
    except Exception as e:
        conn.rollback()
        return {"error": True, "message": str(e), "data": None}
