from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from models import Colors
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/colors", tags=["Colores"])

# Obtener estados de batería
@router.get("", status_code=200, responses={
    404: {"description": "Color no encontrado."},
    500: {"description": "Error interno del servidor."}
})
def get_colors(id: int | None = Query(None, alias="id")):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if id:
            cursor.execute("SELECT * FROM colors WHERE id = %s", (str(id),))
            battery = cursor.fetchall()
            if battery:
                return {
                    "error": False,
                    "message": "OK",
                    "data": [
                        {"id": p[0], "color": p[1]}
                        for p in battery
                    ]
                }
            raise HTTPException(status_code=404, detail="Color no encontrado.")

        cursor.execute("SELECT * FROM colors")
        battery = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {"id": p[0], "color": p[1]}
                for p in battery
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# Crear un color
@router.post("", status_code=201, responses={
    424: {"description": "Error de validación."},
    500: {"description": "Error interno del servidor."}
})
def create_color(color: Colors):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = "INSERT INTO colors (color) VALUES (%s) RETURNING id"
        cursor.execute(query, (color.color,))
        new_id = cursor.fetchone()["id"]
        conn.commit()

        return {
            "error": False,
            "message": "Color creado correctamente.",
            "data": {"id": new_id, "color": color.color}
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el color: " + str(e))
    finally:
        conn.close()