import os
from dotenv import load_dotenv

load_dotenv("config/.env")

class Settings:
    ENV = os.getenv("ENV", "development")

    CLOUD_ROOT = os.getenv("CLOUD_ROOT")
    CLOUD_STORAGE_DIR = os.getenv("CLOUD_STORAGE_DIR")
    CLOUD_LOG_DIR = os.getenv("CLOUD_LOG_DIR")

    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))

settings = Settings()
