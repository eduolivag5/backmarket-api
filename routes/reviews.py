from fastapi import APIRouter, HTTPException, Query
from psycopg2.extras import RealDictCursor
from database import get_db_connection
from uuid import UUID

router = APIRouter(prefix="/reviews", tags=["Reseñas"])

# Obtener reviews
@router.get("", status_code=200, responses={
    404: {"description": "Review no encontrada."},
    500: {"description": "Error interno del servidor."}
})
def get_reviews():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT r.id, r.stars, r.comment, r.image, pr.id as product_id, pr.name_short, u.name as name_user ' \
                'FROM reviews r ' \
                'INNER JOIN products_v2 pr ON r."productId" = pr.id ' \
                'INNER JOIN users u ON r.id_user = u.id;')
        reviews = cursor.fetchall()
        return {
            "error": False,
            "message": "OK",
            "data": [
                {
                    "id": p[0],
                    "stars": p[1],
                    "comment": p[2],
                    "image": p[3],
                    "product_id": p[4],
                    "model": p[5],
                    "name_user": p[6]
                }
                for p in reviews
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

