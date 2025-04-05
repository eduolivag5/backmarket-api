from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection

router = APIRouter(prefix="/battery", tags=["Estados de batería"])

# Obtener estados de batería
@router.get("", status_code=200, responses={
    404: {"description": "Estado de batería no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def get_status(id: int | None = Query(None, alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if id:
            cursor.execute("SELECT * FROM battery_status WHERE id = %s", (str(id),))
            battery = cursor.fetchall()
            if battery:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "estado": p[1], "descripcion": p[2]}
                        for p in battery
                    ]
                }
            raise HTTPException(status_code=404, detail="Estado de batería no encontrado.")

        cursor.execute("SELECT * FROM battery_status")
        battery = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "estado": p[1], "descripcion": p[2]}
                for p in battery
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()