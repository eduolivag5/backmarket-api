from fastapi import APIRouter, HTTPException, Query
from psycopg2.extras import RealDictCursor
from database import get_db_connection
from models import Brand
from uuid import UUID

router = APIRouter(prefix="/brands", tags=["Marcas"])

# Obtener marcas
@router.get("", status_code=200, responses={
    404: {"description": "Marca no encontrada."},
    500: {"description": "Error interno del servidor."}
})
def get_brands(category: int | None = Query(None, alias="category")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if category:
            cursor.execute("SELECT id, marca, img_header FROM brands_v2 WHERE category = %s", (str(category),))
            brands = cursor.fetchall()
            if brands:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "marca": p[1], "img_header": p[2]}
                        for p in brands
                    ]
                }
            raise HTTPException(status_code=404, detail="Marca no encontrada.")

        cursor.execute("SELECT id, marca, img_header FROM brands_v2")
        brands = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "marca": p[1], "img_header": p[2]}
                for p in brands
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Crear una marca
@router.post("", status_code=201, responses={
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def create_brand(brand: Brand):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = "INSERT INTO brands_v2 (marca) VALUES (%s) RETURNING id"
        cursor.execute(query, (brand.marca,))
        new_id = cursor.fetchone()["id"]  # Obtener el ID generado por la BD
        conn.commit()

        return {
            "error": False,
            "message": "Marca creada correctamente",
            "data": {"id": new_id, "marca": brand.marca}
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error al crear marca: " + str(e))
    finally:
        conn.close()

# Actualizar una marca por ID
@router.put("", status_code=200, responses={
    404: {"description": "Marca no encontrada."},
    500: {"description": "Error interno del servidor."}
})
def update_brand(id: int = Query(..., alias="id"), brand: Brand = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar si la marca existe
        cursor.execute("SELECT 1 FROM brands_v2 WHERE id = %s", (str(id),))
        if cursor.fetchone() is None:
            # Si la marca no existe, lanzar error 404
            raise HTTPException(status_code=404, detail="Marca no encontrada.")

        # Proceder con la actualización de la marca
        query = """
            UPDATE brands_v2 
            SET marca = %s
            WHERE id = %s
        """
        values = (brand.marca, str(id))
        cursor.execute(query, values)
        conn.commit()

        # Verificar si la actualización afectó alguna fila
        if cursor.rowcount == 0:
            # Si no se afectó ninguna fila, lanzar error 404
            raise HTTPException(status_code=404, detail="Marca no encontrada.")

        return {"error": False, "message": "Marca actualizada correctamente.", "data": None}

    except HTTPException as http_error:
        # Capturar la excepción HTTPException para que el estado 404 sea manejado adecuadamente
        raise http_error
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

    finally:
        conn.close()



# Eliminar una marca por ID
@router.delete("", status_code=200, responses={
    404: {"description": "Marca no encontrada."},
    500: {"description": "Error interno del servidor."}
})
def delete_brand(id: int = Query(..., alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM brands_v2 WHERE id = %s", (str(id),))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Marca no encontrada.")
        return {"error": False, "message": "Marca eliminada correctamente.", "data": None}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()