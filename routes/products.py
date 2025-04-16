from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from models import Product
from uuid import UUID

router = APIRouter(prefix="/products", tags=["Productos"])


@router.get("", status_code=200, responses={
    404: {"description": "Producto no encontrado."},
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def get_products(id: UUID | None = Query(None, alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        def get_prices(product_id):
            cursor.execute("""
                SELECT ps.estado, pr.price
                FROM prices pr
                JOIN phone_status ps ON pr.status = ps.id
                WHERE pr.id_product = %s
            """, (str(product_id),))
            return [{"status": estado, "price": price} for estado, price in cursor.fetchall()]

        if id:
            # Buscar un producto por ID
            cursor.execute("SELECT * FROM products WHERE id = %s", (str(id),))
            product = cursor.fetchone()
            if product:
                return {
                    "error": False,
                    "message": "OK",
                    "data": {
                        "id": product[0], "created_at": product[1], "marca": product[2],
                        "modelo": product[3], "color": product[4], "almacenamiento": product[5],
                        "fecha_lanzamiento": product[6], "images": product[7], "prices": get_prices(product[0])
                    }
                }
            # Lanzar directamente una excepción HTTP 404 sin capturarla en el except
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Obtener todos los productos
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {
                    "id": p[0], "created_at": p[1], "marca": p[2], "modelo": p[3],
                    "color": p[4], "almacenamiento": p[5], "fecha_lanzamiento": p[6],
                    "images": p[7], "prices": get_prices(p[0])
                } for p in products
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Crear un producto
@router.post("", status_code=201, responses={
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def create_product(product: Product):
    conn = get_db_connection()
    cursor = conn.cursor()

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
        raise HTTPException(status_code=500, detail="Error al crear producto: " + str(e))
    finally:
        conn.close()

# Actualizar un producto por ID
@router.put("", status_code=200, responses={
    404: {"description": "Producto no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def update_product(id: UUID = Query(..., alias="id"), product: Product = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el producto existe
        cursor.execute("SELECT 1 FROM products WHERE id = %s", (str(id),))
        if cursor.fetchone() is None:
            # Si no se encuentra el producto, lanzar un error 404
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        # Si el producto existe, proceder con la actualización
        query = """
            UPDATE products 
            SET marca = %s, modelo = %s, color = %s, almacenamiento = %s, fecha_lanzamiento = %s, image_urls = %s
            WHERE id = %s
        """
        values = (product.marca, product.modelo, product.color, product.almacenamiento, product.fecha_lanzamiento, product.images, str(id))
        cursor.execute(query, values)
        conn.commit()

        # Verificar si la actualización afectó alguna fila
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return {"error": False, "message": "Producto actualizado correctamente", "data": None}

    except HTTPException as e:
        # Capturamos específicamente HTTPException para manejar los errores personalizados
        raise e
    except Exception as e:
        # Si hay otro tipo de error, rollback y lanzamos error 500
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Eliminar un producto por ID
@router.delete("", status_code=200, responses={
    404: {"description": "Producto no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def delete_product(id: UUID = Query(..., alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el producto existe
        cursor.execute("SELECT 1 FROM products WHERE id = %s", (str(id),))
        if cursor.fetchone() is None:
            # Si el producto no existe, lanzar error 404
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        # Proceder con la eliminación del producto
        cursor.execute("DELETE FROM products WHERE id = %s", (str(id),))
        conn.commit()

        # Verificar si la eliminación afectó alguna fila
        if cursor.rowcount == 0:
            # Si no se afectó ninguna fila, lanzar error 404
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        return {"error": False, "message": "Producto eliminado correctamente", "data": None}

    except HTTPException as e:
        # Capturar la excepción HTTPException y lanzar el código correspondiente
        raise e
    except Exception as e:
        # Capturar cualquier otro tipo de error
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor: " + str(e))
    finally:
        conn.close()
