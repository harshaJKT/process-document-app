from fastapi import APIRouter, UploadFile, File, Form
import os
import uuid
from app.messaging import broker
import config

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), role: str = Form(default="Default Role")):
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as out_file:
            content = await file.read()
            out_file.write(content)

        message = {
            "file_path": file_path,
            "original_name": file.filename,
            "role_required": role,
        }
        await broker.publish("doc_uploaded", message)

        return {
            "message": "File uploaded and queued for processing",
            "file_path": file_path,
            "role": role,
        }

    except Exception as e:
        return {"error": str(e)}