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
    """
    Uploads a document and publishes a message to the local message broker for processing.
    """
    try:
        # Ensure uploads directory exists
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)

        # Generate a unique filename
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(config.UPLOAD_DIR, unique_filename)

        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Prepare message for processing
        message = {
            "file_path": file_path,
            "original_filename": file.filename,
            "role": role,
        }

        # Publish message to message broker
        await broker.publish("doc_uploaded", message)

        return {
            "message": "File uploaded and queued for processing",
            "file_path": file_path,
            "role": role,
        }

    except Exception as e:
        return {"error": str(e)}
