import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.database import get_db
from app.models import DocumentData
from fastapi import Depends


def divide_into_chunks(content,chunk_size)->list:
    return [content[i:i+chunk_size] for i in range(0,len(content),chunk_size)]


async def process_document(message):
    """
    TODO: Implement document processing logic
    - Extract file_path and original_name from message
    - Read file content (PDF/text)
    - Chunk content into paragraphs/pages (min 4 chunks)
    - Store each chunk in document_data table with chunk_number
    """

    # These keys should be present in the message while publishing the message to the topic.
    file_path = message["file_path"]
    original_name = message["original_name"]
    role = message.get("role_required", "Analyst")

    print(f"[Worker] Processing file: {original_name} at {file_path}")

    # TODO: Read file content
    content = await read_file_content(file_path)

    # TODO: Chunk content
    chunks = await chunk_content(content)

    # TODO: Store chunks in database
    # store_chunks_in_db(chunks, document_name, role)
    await store_chunks_in_db(chunks , original_name , role)

    print(f"[Worker] Completed processing: {original_name}")


async def read_file_content(file_path):
    """
    TODO: Implement file reading logic
    - Support PDF files using PyPDF2
    - Return file content as string
    """
    try:
        text = ""
        
        with open(file_path,'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text=page.extract_text()
                if page_text:
                    text+=page_text
            return text
    except Exception as e:
        raise e

    


async def chunk_content(content):
    """
    TODO: Implement content chunking logic
    - Split content into paragraphs or pages
    - Ensure size of each chunk is < 100 characters and > 10 characters
    - Return list of chunks
    """
    # TODO: Implement content chunking logic
    chunk_size = 50
    chunks = divide_into_chunks(content,chunk_size)
    return chunks



async def store_chunks_in_db(chunks, document_name, role):
    """
    TODO: Implement database storage logic
    - Create database session
    - For each chunk, create DocumentData record with chunk_number
    - Commit to database
    """
    pass  # TODO: Implement database storage logic
    db:Session = SessionLocal()
    try:

        chunk_number = 1
        for chunk in chunks:
            record = DocumentData(document_name = document_name , chunk_number = chunk_number , chunk_content = chunk , role = role)
            chunk_number+=1
            db.add(record)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

