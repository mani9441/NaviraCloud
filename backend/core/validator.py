import os
import sys

def validate_cloud_mount(cloud_root: str):
    if not os.path.exists(cloud_root):
        print(f"[FATAL] Cloud root does not exist: {cloud_root}")
        sys.exit(1)

    if not os.path.ismount(cloud_root):
        print(f"[FATAL] Cloud root is not mounted: {cloud_root}")
        sys.exit(1)

def ensure_directories(paths: list[str]):
    for path in paths:
        os.makedirs(path, exist_ok=True)
