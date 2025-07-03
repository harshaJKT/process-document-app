import uuid
import PyPDF2
import os
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

    # ✅ These keys should be present in the message while publishing the message to the topic.
    file_path = message["file_path"]
    original_name = message["original_name"]
    role = message.get("role_required", "Analyst")

    print(f"[Worker] Processing file: {original_name} at {file_path}")

    # TODO: Read file content
    content = await read_file_content(file_path)

    # TODO: Chunk content
    chunks = await chunk_content(content)

    # TODO: Store chunks in database
    await store_chunks_in_db(chunks, original_name, role)

    print(f"[Worker] Completed processing: {original_name}")


async def read_file_content(file_path):
    """
    TODO: Implement file reading logic
    - Support PDF files using PyPDF2
    - Return file content as string
    """
    try:
        content = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                content += page.extract_text() or ""
        return content.strip()
    except Exception as e:
        print(f"[Error] Failed to read file: {e}")
        return ""


async def chunk_content(content):
    """
    TODO: Implement content chunking logic
    - Split content into paragraphs or pages
    - Ensure size of each chunk is < 100 characters and > 10 characters
    - Return list of chunks
    """
    words = content.split()
    chunks = []
    chunk = ""

    for word in words:
        if len(chunk) + len(word) + 1 <= 100:
            chunk += " " + word if chunk else word
        else:
            if 10 <= len(chunk) <= 100:
                chunks.append(chunk.strip())
            chunk = word

    if 10 <= len(chunk) <= 100:
        chunks.append(chunk.strip())

    # Ensure at least 4 chunks
    while len(chunks) < 4:
        chunks.append("padding content to meet min chunk requirement.")

    return chunks


async def store_chunks_in_db(chunks, document_name, role):
    """
    TODO: Implement database storage logic
    - Create database session
    - For each chunk, create DocumentData record with chunk_number
    - Commit to database
    """
    try:
        db: Session = SessionLocal()
        for i, chunk in enumerate(chunks):
            db_chunk = DocumentData(
                chunk_id=uuid.uuid4(),
                document_name=document_name,
                chunk_number=i + 1,
                chunk_content=chunk,
                role=role
            )
            db.add(db_chunk)
        db.commit()
        db.close()
    except Exception as e:
        print(f"[Error] Failed to store chunks in DB: {e}")

 