from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, APP_VERSION
from app.database import engine, Base
from app.routes import auth
from app.routes import drivers

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Backend de UrbanGo - Plataforma de Movilidad y Logística"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router)
app.include_router(drivers.router)

@app.get("/")
def root():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "online"
    }

@app.get("/health")
def health():
    return {"status": "ok"}