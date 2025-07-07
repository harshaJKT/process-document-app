from fastapi import APIRouter, UploadFile, File, Form
import os
import uuid
import aiofiles

from app.messaging import broker
from app.logger import setup_logger
import config

router = APIRouter()
logger = setup_logger(f"[{__name__}]")


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    role: str = Form(default="Default Role")
):
    """
    Uploads a document and queues it for background processing.
    
    Steps:
    1. Generate a unique filename.
    2. Save the file to the uploads directory.
    3. Publish a message with file details to the 'doc_uploaded' topic.
    4. Return a success response with file path and role.
    """
    try:
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)

        # Generate unique filename to avoid collisions
        file_path = os.path.join(config.UPLOAD_DIR, file.filename)

        # Save the file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(await file.read())

        # Prepare message for processing
        message = {
            "file_path": file_path,
            "original_name": file.filename,
            "role_required": role,
        }

        await broker.publish("doc_uploaded", message)
        logger.info(f"Uploaded and queued file: {file.filename} for role '{role}'")

        return {
            "message": "File uploaded and queued for processing",
            "file_path": file_path,
            "role": role,
        }

    except Exception as e:
        logger.exception("File upload failed")
        return {"error": str(e)}
