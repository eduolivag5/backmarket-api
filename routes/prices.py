from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from models import Price
from uuid import UUID
from psycopg2 import errors
import psycopg2.extras

router = APIRouter(prefix="/prices", tags=["Precios"])

# Obtener todos los precios
@router.get("", status_code=200, responses={
    404: {"description": "Precio no encontrado."},
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def get_prices(id: UUID | None = Query(None, alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if id:
            cursor.execute("SELECT * FROM prices_v2 WHERE id_product = %s", (str(id),))
            prices = cursor.fetchall()
            if prices:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "id_product": p[1], "status": p[2], "price": p[3]}
                        for p in prices
                    ]
                }
            raise HTTPException(status_code=404, detail="Precio no encontrado.")

        cursor.execute("SELECT * FROM prices_v2")
        prices = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "id_product": p[1], "status": p[2], "price": p[3]}
                for p in prices
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Crear un precio
@router.post("", status_code=201, responses={
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def create_price(price: Price):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        # Verificar si ya existe una combinación de id_product y status
        check_query = """
            SELECT id FROM prices_v2 WHERE id_product = %s AND status = %s
        """
        cursor.execute(check_query, (str(price.id_product), price.status))
        existing_price = cursor.fetchone()

        if existing_price:
            raise HTTPException(
                status_code=424,
                detail=f"Ya existe esa combinación de precios para ese producto."
            )

        # Insertar nuevo precio
        insert_query = """
            INSERT INTO prices_v2 (id_product, status, price) 
            VALUES (%s, %s, %s) RETURNING id
        """
        values = (str(price.id_product), price.status, price.price)
        cursor.execute(insert_query, values)
        new_id = cursor.fetchone()["id"]
        conn.commit()
        price.id = new_id

        return {
            "error": False,
            "message": "Precio creado correctamente.",
            "data": {"id": new_id, "price": price}
        }


    except errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(status_code=424, detail="El producto no existe.")

    except HTTPException as e:
        raise e  # <-- Añadir esta línea

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error al crear precio: " + str(e))

    finally:
        conn.close()



# Actualizar un precio por ID
@router.put("", status_code=200, responses={
    404: {"description": "Precio no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def update_product_price(price: Price = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE prices_v2 
            SET price = %s
            WHERE id_product = %s and status = %s
        """
        values = (price.price, str(price.id_product), price.status)
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Opción de producto no encontrado.")
        return {"error": False, "message": "Precio actualizado correctamente.", "data": None}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Eliminar un precio o todos los precios de un producto por ID
@router.delete("", status_code=200, responses={
    404: {"description": "Precio no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def delete_price(id: UUID = Query(None, alias="id"), id_product: UUID = Query(None, alias="id_product")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if id_product:
            # Eliminar todos los precios de un producto específico
            cursor.execute("DELETE FROM prices_v2 WHERE id_product = %s", (str(id_product),))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="No se encontraron precios para este producto.")
            return {"error": False, "message": "Precios del producto eliminados correctamente.", "data": None}

        if id:
            # Eliminar un precio específico por ID
            cursor.execute("DELETE FROM prices_v2 WHERE id = %s", (str(id),))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Precio no encontrado.")
            return {"error": False, "message": "Precio eliminado correctamente.", "data": None}

        raise HTTPException(status_code=400, detail="Debe proporcionar un 'id' o 'id_product'.")

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        conn.close()
