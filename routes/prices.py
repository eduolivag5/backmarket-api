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
            cursor.execute("SELECT * FROM prices WHERE id_product = %s", (str(id),))
            prices = cursor.fetchall()
            if prices:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "id_product": p[1], "status": p[2], "battery": p[3], "price": p[4]}
                        for p in prices
                    ]
                }
            raise HTTPException(status_code=404, detail="Precio no encontrado.")

        cursor.execute("SELECT * FROM prices")
        prices = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "id_product": p[1], "status": p[2], "battery": p[3], "price": p[4]}
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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # Usar DictCursor para acceder a las columnas por nombre

    try:
        query = """
            INSERT INTO prices (id_product, status, battery, price) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        values = (str(price.id_product), price.status, price.battery, price.price)
        cursor.execute(query, values)
        new_id = cursor.fetchone()["id"]  # Acceder al 'id' correctamente usando DictCursor
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
def update_price(id: UUID = Query(..., alias="id"), price: Price = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE prices 
            SET id_product = %s, status = %s, battery = %s, price = %s
            WHERE id = %s
        """
        values = (str(price.id_product), price.status, price.battery, price.price, str(id))
        cursor.execute(query, values)
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Precio no encontrado.")
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
            cursor.execute("DELETE FROM prices WHERE id_product = %s", (str(id_product),))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="No se encontraron precios para este producto.")
            return {"error": False, "message": "Precios del producto eliminados correctamente.", "data": None}

        if id:
            # Eliminar un precio específico por ID
            cursor.execute("DELETE FROM prices WHERE id = %s", (str(id),))
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
