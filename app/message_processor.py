import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.database import SessionLocal 
from app.models import DocumentData
from io import BytesIO

MIN_CHAR = 10
MAX_CHAR = 100
# comment
# comment 2
# comment 3
# comment 4

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
    await store_chunks_in_db(chunks,original_name,role)
    # store_chunks_in_db(chunks, document_name, role)

    print(f"[Worker] Completed processing: {original_name}")


async def read_file_content(file_path):
    """
    TODO: Implement file reading logic
    - Support PDF files using PyPDF2
    - Return file content as string
    """

    data = None
    async with aiofiles.open(file_path,'rb') as f:
        data = await f.read()

    reader = PyPDF2.PdfReader(BytesIO(data))
    content = "\n".join([page.extract_text() or "" for page in reader.pages])
    return content



async def chunk_content(content : str):
    """
    TODO: Implement content chunking logic
    - Split content into paragraphs or pages
    - Ensure size of each chunk is < 100 characters and > 10 characters
    - Return list of chunks
    """
    # TODO: Implement content chunking logic
    chunks : list[str] = []
    paragraphs = content.split("\n")

    for para in paragraphs:
        para = para.strip()

        while len(para) > MAX_CHAR:
            part = para[:MAX_CHAR]
            split_idx = part.rfind(" ")
            if split_idx > MIN_CHAR:
                part = para[:split_idx]
                para = para[split_idx:].strip()
            else :
                part = para[:MAX_CHAR]
                para = para[MAX_CHAR:].strip()
            chunks.append(part)

        if MIN_CHAR < len(para) < MAX_CHAR:
            chunks.append(para)
    
    return chunks


async def add_keywords_in_chunks(chunks : list[str]) -> list[str]:
    # TODO add keywords in chunks
    pass

async def store_chunks_in_db(chunks : list[str], document_name : str, role : str):
    """
    TODO: Implement database storage logic
    - Create database session
    - For each chunk, create DocumentData record with chunk_number
    - Commit to database
    """
    # TODO: Implement database storage logic

    try:
        db : Session = SessionLocal()

        db_chunks = [DocumentData(
            chunk_id=uuid.uuid4(),
            document_name=document_name,
            role=role,
            chunk_number=chunk_number,
            chunk_content=chunk
        ) for chunk_number,chunk in enumerate(chunks,start=1)]

        db.add_all(db_chunks)
        db.commit()
    
    finally:
        db.close()


