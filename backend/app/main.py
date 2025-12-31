from fastapi import FastAPI
from config.settings import settings
from core.validator import validate_cloud_mount, ensure_directories

app = FastAPI(title="MyCloudHub")

@app.on_event("startup")
def startup_checks():
    validate_cloud_mount(settings.CLOUD_ROOT)
    ensure_directories([
        settings.CLOUD_STORAGE_DIR,
        settings.CLOUD_LOG_DIR,
    ])

@app.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.ENV
    }
