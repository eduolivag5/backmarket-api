from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from models import Product
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/products", tags=["Productos"])


@router.get("", status_code=200, responses={
    404: {"description": "Producto no encontrado."},
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def get_products(
    id: Optional[UUID] = Query(None, alias="id"),
    category: Optional[str] = Query(None, alias="category"),
    tags: Optional[str] = Query(None, alias="tags")  # Ej: "iphone,movil,apple"
):
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
            cursor.execute("SELECT * FROM products_v2 WHERE id = %s", (str(id),))
            product = cursor.fetchone()
            if product:
                return {
                    "error": False,
                    "message": "OK",
                    "data": {
                        "id": product[0], "created_at": product[1], "category": product[2],
                        "brand": product[3], "name_short": product[4], "name": product[5], "colors": product[6],
                        "storages": product[7], "images": product[8], "tags": product[9], "prices": get_prices(product[0])
                    }
                }
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Armar query dinámico
        query = "SELECT * FROM products_v2"
        filters = []
        values = []

        if category:
            filters.append("category = %s")
            values.append(category)

        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            if tag_list:
                # usamos operador && para arrays que tengan intersección
                filters.append("tags && %s::text[]")
                values.append(tag_list)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        cursor.execute(query, tuple(values))
        products = cursor.fetchall()

        return {
            "error": False,
            "message": "OK",
            "data": [
                {
                    "id": product[0], "created_at": product[1], "category": product[2],
                    "brand": product[3], "name_short": product[4], "name": product[5], "colors": product[6],
                    "storages": product[7], "images": product[8], "tags": product[9], "prices": get_prices(product[0])
                } for product in products
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.post("", status_code=201, responses={
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def create_product(product: Product):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si el nombre del producto ya existe
        check_query = """
            SELECT 1 FROM products_v2 WHERE name = %s OR name_short = %s
        """
        cursor.execute(check_query, (product.name, product.name_short))
        existing_product = cursor.fetchone()

        if existing_product:
            raise HTTPException(status_code=424, detail="Ya existe un producto con el mismo nombre o nombre corto")

        # Si no existe, proceder con la inserción
        insert_query = """
            INSERT INTO products_v2 (category, brand, name_short, name, colors, storages, images, tags) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = (product.category, product.brand, product.name_short, product.name, product.colors,
                  product.storages, product.images, product.tags
                  )
        cursor.execute(insert_query, values)
        new_id = cursor.fetchone()[0]  # Obtener el ID generado
        conn.commit()

        return {
            "error": False,
            "message": "Producto creado correctamente",
            "data": {
                **product.model_dump(),
                "id": new_id
            }
        }
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
        cursor.execute("SELECT 1 FROM products_v2 WHERE id = %s", (str(id),))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        # Actualizar el producto
        query = """
            UPDATE products_v2
            SET category = %s, brand = %s, name_short = %s, name = %s,
                colors = %s, storages = %s, images = %s, tags = %s
            WHERE id = %s
        """
        values = (
            product.category, product.brand, product.name_short, product.name,
            product.colors, product.storages, product.images, product.tags, str(id)
        )
        cursor.execute(query, values)
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return {"error": False, "message": "Producto actualizado correctamente", "data": None}

    except HTTPException as e:
        raise e
    except Exception as e:
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
        cursor.execute("SELECT 1 FROM products_v2 WHERE id = %s", (str(id),))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        # Eliminar el producto
        cursor.execute("DELETE FROM products_v2 WHERE id = %s", (str(id),))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")

        return {"error": False, "message": "Producto eliminado correctamente", "data": None}

    except HTTPException as e:
        raise e
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor: " + str(e))
    finally:
        conn.close()
