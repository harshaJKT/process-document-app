from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os
import uuid
from app.messaging import broker
import config
 
router = APIRouter()
 
 
@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...), role: str = Form(default="Default Role")
):
    try:
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        save_path = os.path.join(config.UPLOAD_DIR, unique_filename)
 
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
 
        message = {
            "file_path": save_path,
            "original_name": file.filename,
            "role_required": role
        }
 
        await broker.publish("doc_uploaded", message)
 
        return {
            "message": "File uploaded and queued for processing",
            "file_path": save_path,
            "role": role,
        }
    except Exception as e:
        return {"error": str(e)}
