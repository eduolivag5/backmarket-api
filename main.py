import os
import psycopg2
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from routes import products, prices, brands, phone_status, reviews, categories
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

# Cargar variables de entorno
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Conectar a PostgreSQL
conn = psycopg2.connect(
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    dbname=DBNAME
)
cursor = conn.cursor()

# Crear aplicación FastAPI
app = FastAPI(
    title="API BackMarket",
    description="Esta API permite gestionar productos y precios en una base de datos PostgreSQL.",
    version="1.0.0",
    contact={
        "name": "Eduardo Oliva Garcia",
        "email": "eduolivag5@gmail.com",
    },
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "data": None
        },
    )


app.include_router(products.router)
app.include_router(prices.router)
app.include_router(brands.router)
app.include_router(phone_status.router)
app.include_router(reviews.router)
app.include_router(categories.router)