import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.database import SessionLocal 
from app.models import DocumentData
from io import BytesIO
from app.utils.llm_chat import ask_llm

MIN_CHAR = 10
MAX_CHAR = 100

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
    print(f"[Worker] Content : content")
    # TODO: Chunk content
    chunks = await chunk_content(content)
    print(f"[Worker] Chunks : chunks")

    # add keyword and summary here
    enriched_chunks = await enrich_chunks_with_llm(chunks)
    print(f"[Worker] Enriched Chuncks : {enriched_chunks}")

    # TODO: Store chunks in database
    await store_chunks_in_db(enriched_chunks,original_name,role)
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



async def chunk_content(content: str):
    """
    Split content into chunks:
    - Each chunk has at least 100 words
    - Each chunk ends at a sentence boundary (after a '.')
    """
    MIN_WORDS = 100
    chunks = []
    words = content.split()
    
    current_chunk = []
    word_count = 0

    for word in words:
        current_chunk.append(word)
        word_count += 1

        if word.endswith('.') and word_count >= MIN_WORDS:
            chunk_text = " ".join(current_chunk).strip()
            chunks.append(chunk_text)
            current_chunk = []
            word_count = 0

    # Add remaining words as the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks



async def enrich_chunks_with_llm(chunks: list[str]) -> list[dict]:
    """
    Processes each chunk with LLM to get keywords and summary.
    Returns list of dicts: { "content": ..., "keywords": ..., "summary": ... }
    """
    enriched = []

    for chunk in chunks:
        llm_response = ask_llm(
            question="Generate 3 keywords and a 1-line summary.",
            context=chunk,
            response_format={
                "keywords": ["k1", "k2", "k3"],
                "summary": "one-line summary"
            }
        )
        print(f"for chunk {chunk}, llm response:{llm_response}")
        enriched.append({
            "content": chunk,
            "keywords": "\n".join(llm_response.get("keywords", [])),
            "summary": llm_response.get("summary", "")
        })

    return enriched



async def store_chunks_in_db(enriched_chunks: list[dict], document_name: str, role: str):
    try:
        db: Session = SessionLocal()
        db_chunks = []

        for chunk_number, item in enumerate(enriched_chunks, start=1):
            db_chunks.append(DocumentData(
                chunk_id=uuid.uuid4(),
                document_name=document_name,
                role=role,
                chunk_number=chunk_number,
                chunk_content=item["content"],
                keywords=item["keywords"],
                summary=item["summary"]
            ))

        db.add_all(db_chunks)
        db.commit()

    finally:
        db.close()



