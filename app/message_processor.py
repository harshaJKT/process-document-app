import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData


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

     
    print(f"[Worker] Completed processing: {original_name}")


async def read_file_content(file_path):
    """
    TODO: Implement file reading logic
    - Support PDF files using PyPDF2
    - Return file content as string
    """


async def chunk_content(content):
    """
    TODO: Implement content chunking logic
    - Split content into paragraphs or pages
    - Ensure size of each chunk is < 100 characters and > 10 characters
    - Return list of chunks
    """
    pass  


async def store_chunks_in_db(chunks, document_name, role):
    """
    TODO: Implement database storage logic
    - Create database session
    - For each chunk, create DocumentData record with chunk_number
    - Commit to database
    """
    pass  
import uuid
import PyPDF2
import os
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData


def divide_into_chunks(content, chunk_size) -> list:
    return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]


async def process_document(message):
    """
    Main processing logic for uploaded document.
    """
    file_path = message["file_path"]
    original_name = message["original_filename"]
    role = message.get("role", "Analyst")

    print(f"[Worker] Processing file: {original_name} at {file_path}")

    # 1. Read content
    content = await read_file_content(file_path)

    # 2. Chunk content
    chunks = await chunk_content(content)

    # 3. Store chunks in DB
    await store_chunks_in_db(chunks, original_name, role)

    print(f"[Worker] Completed processing: {original_name}")


async def read_file_content(file_path):
    """
    Reads PDF content using PyPDF2.
    """
    try:
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Error reading file: {e}")


async def chunk_content(content):
    """
    Splits content into chunks (10–100 characters), minimum 4 chunks.
    """
    chunk_size = 50
    chunks = divide_into_chunks(content, chunk_size)
    
    # Ensure minimum 4 chunks
    if len(chunks) < 4:
        avg_len = max(10, len(content) // 4)
        chunks = [content[i:i+avg_len] for i in range(0, len(content), avg_len)]

    return chunks


async def store_chunks_in_db(chunks, document_name, role):
    """
    Stores each chunk into the document_data table.
    """
    db: Session = SessionLocal()
    try:
        for idx, chunk in enumerate(chunks):
            record = DocumentData(
                chunk_id=uuid.uuid4(),
                document_name=document_name,
                chunk_number=idx + 1,
                chunk_content=chunk,
                role=role,
            )
            db.add(record)

        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"DB insert error: {e}")
    finally:
        db.close()
