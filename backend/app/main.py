from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from config.settings import settings
from core.validator import validate_cloud_mount, ensure_directories
from core.storage.file_manager import FileManager
import os
from fastapi import Depends
from core.auth.deps import get_current_user
from core.db.session import init_db
from api.users import router as users_router

app = FastAPI(title="naviracloud v1")

app.include_router(users_router)

# Startup checks
@app.on_event("startup")
def startup_checks():
    validate_cloud_mount(settings.CLOUD_ROOT)
    ensure_directories([
        settings.CLOUD_STORAGE_DIR,
        settings.CLOUD_LOG_DIR
    ])
    init_db()

file_manager = FileManager(settings.CLOUD_STORAGE_DIR)

# ----- Upload File -----
@app.post("/files")
async def upload_file(file: UploadFile = File(...), folder: str = "", current_user=Depends(get_current_user)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    dest = file_manager.save_file(str(current_user.id), folder, file.filename, temp_path)
    os.remove(temp_path)
    return {"message": "File uploaded", "path": str(dest)}

# ----- List Files -----
@app.get("/files")
def list_files(folder: str = "", current_user=Depends(get_current_user)):
    return {"files": file_manager.list_files(str(current_user.id), folder)}

# ----- Download File -----
@app.get("/files/download")
def download_file(filename: str, folder: str = "", version: int = 0, current_user=Depends(get_current_user)):
    try:
        if version == 0:
            path = file_manager.get_latest_file(str(current_user.id), folder, filename)
        else:
            path = file_manager.get_file_by_version(str(current_user.id), folder, filename, version)
        return FileResponse(path, media_type="application/octet-stream", filename=path.name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

# ===== Health Check =====
@app.get("/health")
def health():
    return {"status": "ok"}
