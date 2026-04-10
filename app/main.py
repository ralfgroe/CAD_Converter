import os
import uuid
import logging

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.converter import convert_step_to_obj

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="STEP to OBJ Converter")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/convert")
async def convert(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".step", ".stp"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload a .step or .stp file.",
        )

    file_id = uuid.uuid4().hex
    original_stem = os.path.splitext(file.filename)[0]

    step_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    obj_path = os.path.join(OUTPUT_DIR, f"{file_id}.obj")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 100 MB)")

    with open(step_path, "wb") as f:
        f.write(content)

    logger.info("Uploaded %s as %s (%d bytes)", file.filename, file_id, len(content))

    try:
        result = convert_step_to_obj(step_path, obj_path)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if os.path.isfile(step_path):
            os.remove(step_path)

    return {
        "file_id": file_id,
        "original_name": file.filename,
        "obj_filename": f"{original_stem}.obj",
        "file_size_bytes": result.file_size_bytes,
        "vertex_count": result.vertex_count,
        "face_count": result.face_count,
    }


@app.get("/api/preview/{file_id}")
async def preview(file_id: str):
    obj_path = os.path.join(OUTPUT_DIR, f"{file_id}.obj")
    if not os.path.isfile(obj_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(obj_path, media_type="text/plain")


@app.get("/api/download/{file_id}")
async def download(file_id: str):
    obj_path = os.path.join(OUTPUT_DIR, f"{file_id}.obj")
    if not os.path.isfile(obj_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        obj_path,
        media_type="application/octet-stream",
        filename=f"{file_id}.obj",
    )
