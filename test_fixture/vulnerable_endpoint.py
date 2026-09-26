import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/files/{file_path:path}")
async def read_file(file_path: str):
    """Read a file from the allowed upload directory with containment."""
    base = "/tmp/uploads"
    base_real = os.path.realpath(base)
    full = os.path.realpath(os.path.join(base, file_path))
    if not full.startswith(base_real + os.sep):
        raise ValueError("Path escape rejected: resolved path outside base directory")
    return open(full).read()
