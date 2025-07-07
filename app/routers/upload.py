from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os
import uuid
from app.messaging import broker
import config

router = APIRouter()

def generate_unique_filename(extension="txt"):
    unique_name = f"{uuid.uuid4()}.{extension}"
    return unique_name


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

        upload_directory = "uploads"

        if not os.path.exists(upload_directory):
            os.makedirs(upload_directory)

        
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        destination_file_path = os.path.join(upload_directory, unique_filename)
        with open(destination_file_path, "wb") as buffer:
            contents = await file.read()  # read the uploaded file content
            buffer.write(contents) 

        # TODO: Publish message to topic for processing
        # Messaging is already implemented in the messaging.py file, refer to it and use it.
        # Think of all the keys that should be present in the message while publishing the message to the topic.
        # Use: await broker.publish("doc_uploaded", message)

        message =  {
            "message": "File uploaded and queued for processing",
            "file_path": destination_file_path,  # TODO: file_path
            "role_required": role.lower(),
            "original_name":file.filename
        }

        await broker.publish("doc_uploaded",message )
        return message

    except Exception as e:
        return {"error": str(e)}
