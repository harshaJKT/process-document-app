import uuid
import PyPDF2
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData
from app.ollama_utils import generate_keywords, summarize_text

async def store_chunks_in_db(chunks, document_name, role):
    from app.database import SessionLocal
    from app.models import DocumentData
    db = SessionLocal()
    try:
        for idx, chunk in enumerate(chunks):
            print(f"[DEBUG] Processing chunk {idx+1}: {chunk[:50]}...")
            keywords = generate_keywords(chunk)
            print(f"[OLLAMA] Keywords: {keywords}")
            summary = summarize_text(chunk)
            print(f"[OLLAMA] Summary: {summary}")
            doc_chunk = DocumentData(
                document_name=document_name,
                chunk_number=idx + 1,
                chunk_content=chunk,
                role=role,
                keywords=keywords,
                summary=summary
            )
            db.add(doc_chunk)
        db.commit()
    finally:
        db.close()

        
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
    role = message["role_required"]

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

 