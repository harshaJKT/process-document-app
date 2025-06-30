from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os
import uuid
from app.messaging import broker
import config
import aiofiles

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...), role: str = Form(default="Default Role")
):
    """
    TODO: Implement file upload logic
    - Create unique file name using uuid
    - Save file to uploads directory
    - Publish message to doc_uploaded topic
    - Return success response
    """
    try:
        # TODO: Save file locally
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(config.UPLOAD_DIR,file.filename)
        async with aiofiles.open(file_path,'wb') as f:
            await f.write(await file.read())
        # TODO: Publish message to topic for processing
        # Messaging is already implemented in the messaging.py file, refer to it and use it.
        # Think of all the keys that should be present in the message while publishing the message to the topic.
        # Use: await broker.publish("doc_uploaded", message)
        message = {
            "file_path" : file_path,
            "original_name" : file.filename,
            "role_required" : role,
        }
        await broker.publish("doc_uploaded",message)

        return {
            "message": "File uploaded and queued for processing",
            "file_path": file_path,  # TODO: file_path
            "role": role,
        }

    except Exception as e:
        return {"error": str(e)}
