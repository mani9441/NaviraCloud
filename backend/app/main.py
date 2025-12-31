from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from config.settings import settings
from core.validator import validate_cloud_mount, ensure_directories
from core.storage.file_manager import FileManager
import os

app = FastAPI(title="MyCloudHub v1")

# Startup checks
@app.on_event("startup")
def startup_checks():
    validate_cloud_mount(settings.CLOUD_ROOT)
    ensure_directories([
        settings.CLOUD_STORAGE_DIR,
        settings.CLOUD_LOG_DIR
    ])

file_manager = FileManager(settings.CLOUD_STORAGE_DIR)

# ===== File Upload =====
@app.post("/files")
async def upload_file(user_id: str, folder: str = "", file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    dest = file_manager.save_file(user_id, folder, file.filename, temp_path)
    os.remove(temp_path)
    return {"message": "File uploaded", "path": str(dest)}

# ===== List Files =====
@app.get("/files")
def list_files(user_id: str, folder: str = ""):
    return {"files": file_manager.list_files(user_id, folder)}

# ===== Download File =====
@app.get("/files/download")
def download_file(user_id: str, folder: str, filename: str, version: int = 0):
    try:
        if version == 0:
            path = file_manager.get_latest_file(user_id, folder, filename)
        else:
            path = file_manager.get_file_by_version(user_id, folder, filename, version)
        return FileResponse(path, media_type="application/octet-stream", filename=path.name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

# ===== Health Check =====
@app.get("/health")
def health():
    return {"status": "ok"}
