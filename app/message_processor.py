import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData
import re
 
CHUNK_MIN = 10
CHUNK_MAX = 100
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
    role = message["role"]
 
    print(f"[Worker] Processing file: {original_name} at {file_path}")
 
    # TODO: Read file content
    content=await read_file_content(file_path)
    if not content:
        print(f"[worker] no content found in {original_name}")
        return
    # TODO: Chunk content
    chunks=await chunk_content(content)
    if len(chunks)<4:
        print(f"[Worker] No content found in {original_name}")
        return  
    # TODO: Store chunks in database
    await store_chunks_in_db(chunks, original_name, role)
 
    print(f"[Worker] Completed processing: {original_name}")
 
 
async def read_file_content(file_path):
    """
    TODO: Implement file reading logic
    - Support PDF files using PyPDF2
    - Return file content as string
    """
    text=""
    with open(file_path,"rb") as f:
        reader=PyPDF2.PdfReader(f)
        for page in reader.pages:
            text+=page.extract_text() or ""
    return text
 
 
async def chunk_content(content):
    """
    TODO: Implement content chunking logic
    - Split content into paragraphs or pages
    - Ensure size of each chunk is < 100 characters and > 10 characters
    - Return list of chunks
    """
    paragraphs = [
        p.strip() for p in re.split(r'\n\s*\n', content)
        if p.strip()
    ]

    chunks = []

    for para in paragraphs:
        # While paragraph is longer than CHUNK_MAX, carve off pieces
        while len(para) > CHUNK_MAX:
            # Try to break at the last space before 100 chars
            split_at = para.rfind(" ", 0, CHUNK_MAX)
            if split_at == -1 or split_at < CHUNK_MIN:
                # No good space → hard split at CHUNK_MAX
                split_at = CHUNK_MAX
            part = para[:split_at].strip()
            if len(part) > CHUNK_MIN:
                chunks.append(part)
            para = para[split_at:].strip()
        
        if CHUNK_MIN < len(para) <= CHUNK_MAX:
            chunks.append(para)
    return chunks  # TODO: Implement content chunking logic
 
 
async def store_chunks_in_db(chunks, document_name, role):
    """
    TODO: Implement database storage logic
    - Create database session
    - For each chunk, create DocumentData record with chunk_number
    - Commit to database
    """
    db:Session=SessionLocal()
    for idx,chunk in enumerate(chunks):
        doc_data=DocumentData(
            document_name=document_name,
            chunk_number=idx+1,
            chunk_content=chunk,
            role=role
        )
    db.add(doc_data)
    db.commit()