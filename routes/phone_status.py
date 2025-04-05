from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from uuid import UUID

router = APIRouter(prefix="/phone_status", tags=["Estados de venta"])

# Obtener estados de venta
@router.get("", status_code=200, responses={
    404: {"description": "Estado de venta no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def get_status(id: int | None = Query(None, alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if id:
            cursor.execute("SELECT * FROM phone_status WHERE id = %s", (str(id),))
            phone_status = cursor.fetchall()
            if phone_status:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "estado": p[1], "descripcion": p[2]}
                        for p in phone_status
                    ]
                }
            raise HTTPException(status_code=404, detail="Estado de venta no encontrado.")

        cursor.execute("SELECT * FROM phone_status")
        phone_status = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "estado": p[1], "descripcion": p[2]}
                for p in phone_status
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()