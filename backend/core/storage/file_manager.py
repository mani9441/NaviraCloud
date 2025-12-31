import os
import shutil
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session
from core.db.models import File


class FileManager:
    def __init__(self, storage_root: str):
        self.storage_root = Path(storage_root)
        if not self.storage_root.exists():
            raise RuntimeError(f"Storage root does not exist: {self.storage_root}")

    def get_user_folder(self, user_id: str, folder: str = "") -> Path:
        path = self.storage_root / str(user_id) / folder
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_file_versions(self, user_id: str, folder: str, filename: str) -> List[Path]:
        file_dir = self.get_user_folder(user_id, folder) / filename
        if not file_dir.exists():
            return []
        return sorted(file_dir.iterdir())  # sorted by version

    def save_file(self, db: Session, user_id: str, folder: str, filename: str, source_path: str) -> Path:
        user_folder = self.get_user_folder(user_id, folder)
        file_dir = user_folder / filename
        file_dir.mkdir(exist_ok=True)
        
        existing_versions = [f for f in file_dir.iterdir() if f.is_file()]
        next_version = len(existing_versions) + 1
        dest_path = file_dir / f"v{next_version}_{filename}"
        shutil.copy2(source_path, dest_path)

        # Insert metadata into DB
        size = os.path.getsize(dest_path)
        db_file = File(
            user_id=int(user_id),
            filename=filename,
            folder=folder,
            version=next_version,
            size=size
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return dest_path
    
    
    def list_files(self, user_id: str, folder: str = "") -> List[str]:
        user_folder = self.get_user_folder(user_id, folder)
        if not user_folder.exists():
            return []
        return [f.name for f in user_folder.iterdir() if f.is_dir()]  # directories are file names

    def get_latest_file(self, user_id: str, folder: str, filename: str) -> Path:
        versions = self.get_file_versions(user_id, folder, filename)
        if not versions:
            raise FileNotFoundError(f"{filename} not found")
        return versions[-1]  # latest

    def get_file_by_version(self, user_id: str, folder: str, filename: str, version: int) -> Path:
        versions = self.get_file_versions(user_id, folder, filename)
        if not versions or version < 1 or version > len(versions):
            raise FileNotFoundError(f"{filename} version {version} not found")
        return versions[version-1]
