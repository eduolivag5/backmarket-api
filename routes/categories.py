from fastapi import APIRouter, HTTPException, Query
from psycopg2.extras import RealDictCursor
from database import get_db_connection
from models import Category
from uuid import UUID

router = APIRouter(prefix="/categories", tags=["Categorias"])

# Obtener categorias
@router.get("", status_code=200, responses={
    404: {"description": "Categoria no encontrada."},
    500: {"description": "Error interno del servidor."}
})
def get_brands(id: int | None = Query(None, alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if id:
            cursor.execute("SELECT * FROM categories WHERE id = %s", (str(id),))
            brands = cursor.fetchall()
            if brands:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "category": p[1]}
                        for p in brands
                    ]
                }
            raise HTTPException(status_code=404, detail="Categoria no encontrada.")

        cursor.execute("SELECT * FROM categories")
        brands = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "category": p[1]}
                for p in brands
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()