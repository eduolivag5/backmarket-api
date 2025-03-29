import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

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
app = FastAPI()

# Modelo de datos para productos
class Product(BaseModel):
    marca: str
    modelo: str
    color: int
    almacenamiento: int
    fecha_lanzamiento: str

# Modelo de datos para precios
class Price(BaseModel):
    id: str
    id_product: int
    status: int
    battery: int
    precio: float

# Endpoint para obtener todos los productos
@app.get("/products")
def get_products():
    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return [
            {
                "id": p[0],
                "created_at": p[1],
                "marca": p[2],
                "modelo": p[3],
                "color": p[4],
                "almacenamiento": p[5],
                "fecha_lanzamiento": p[6]
            }
            for p in products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener productos: " + str(e))

# Endpoint para obtener un producto por ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    try:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if product:
            return {
                "id": product[0],
                "created_at": product[1],
                "marca": product[2],
                "modelo": product[3],
                "color": product[4],
                "almacenamiento": product[5],
                "fecha_lanzamiento": product[6]
            }
        else:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener producto: " + str(e))

# Endpoint para obtener todos los precios
@app.get("/prices")
def get_prices():
    try:
        cursor.execute("SELECT * FROM prices")
        prices = cursor.fetchall()
        return [
            {
                "id": p[0],
                "id_product": p[1],
                "status": p[2],
                "battery": p[3],
                "price": p[4]
            }
            for p in prices
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener precios: " + str(e))

# Endpoint para obtener un precio por ID de producto
@app.get("/prices/{product_id}")
def get_price_by_product(product_id: int):
    try:
        cursor.execute("SELECT * FROM prices WHERE id_product = %s", (product_id,))
        price = cursor.fetchall()
        if price:
            return [
                {
                    "id": p[0],
                    "id_product": p[1],
                    "status": p[2],
                    "battery": p[3],
                    "price": p[4]
                }
                for p in price
            ]
        else:
            raise HTTPException(status_code=404, detail="Precio no encontrado para este producto")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener precios: " + str(e))

# Endpoint para obtener todos los colores
@app.get("/colors")
def get_colors():
    try:
        cursor.execute("SELECT * FROM colors")
        colors = cursor.fetchall()
        return [
            {
                "id": c[0],
                "color": c[1]
            }
            for c in colors
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener colores: " + str(e))

# Endpoint para obtener todos los estados de la batería
@app.get("/battery_status")
def get_battery_status():
    try:
        cursor.execute("SELECT * FROM battery_status")
        battery_status = cursor.fetchall()
        return [
            {
                "id": b[0],
                "estado": b[1],
                "descripcion": b[2]
            }
            for b in battery_status
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener estados de la batería: " + str(e))

# Endpoint para obtener todos los estados de los teléfonos
@app.get("/phone_status")
def get_phone_status():
    try:
        cursor.execute("SELECT * FROM phone_status")
        phone_status = cursor.fetchall()
        return [
            {
                "id": p[0],
                "estado": p[1],
                "descripcrion": p[2]
            }
            for p in phone_status
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener estados de los teléfonos: " + str(e))

# Endpoint para obtener todas las marcas
@app.get("/brands")
def get_brands():
    try:
        cursor.execute("SELECT * FROM brands")
        brands = cursor.fetchall()
        return [
            {
                "id": b[0],
                "marca": b[1]
            }
            for b in brands
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener marcas: " + str(e))

# Endpoint para crear un nuevo producto
@app.post("/products")
def create_product(product: Product):
    try:
        cursor.execute(
            """
            INSERT INTO products (marca, modelo, color, almacenamiento, fecha_lanzamiento)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (product.marca, product.modelo, product.color, product.almacenamiento, product.fecha_lanzamiento)
        )
        new_product_id = cursor.fetchone()[0]
        conn.commit()
        return {"id": new_product_id, "modelo": product.modelo, "estado": product.estado, "color": product.color}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al crear producto: " + str(e))

