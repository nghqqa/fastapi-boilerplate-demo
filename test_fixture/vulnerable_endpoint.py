import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/files/{file_path:path}")
async def read_file(file_path: str):
    base = "/tmp/uploads"
    full = os.path.join(base, file_path)  # CWE-22: no containment
    return open(full).read()
