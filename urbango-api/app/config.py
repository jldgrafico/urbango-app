import os
from dotenv import load_dotenv

load_dotenv()

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:1234@localhost/urbango_db")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "urbango-secret-key-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# App
APP_NAME = "UrbanGo API"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "True") == "True"