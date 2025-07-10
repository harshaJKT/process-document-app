import uuid
import os
import asyncio
import aiofiles
import PyPDF2
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app.database import SessionLocal
from app.models import DocumentData
from app.utils.llm_chat import ask_llm
from app.logger import setup_logger

logger = setup_logger(f"[{__name__}] [Worker]")



async def process_document(message: dict):
    """
    Main document processing pipeline:
    1. Extract file path, name, and role from message.
    2. Read file content (PDF).
    3. Chunk content into ~100-word blocks at sentence boundaries.
    4. Enrich each chunk with keywords and summary using LLM.
    5. Store enriched chunks in the database.
    """
    try:
        file_path = message["file_path"]
        original_name = message["original_name"]
        role = message.get("role_required", "Analyst")
    except KeyError as e:
        logger.error(f"Missing key in message: {e}")
        return

    logger.info(f"Started processing: {original_name}")

    if await check_document_exists(original_name, role):
        logger.warning(f"Document '{original_name}' with role '{role}' already exists. Skipping processing.")
        return

    content = await read_file_content(file_path)
    logger.info("File content read successfully.")

    chunks = await chunk_content(content)
    logger.info(f"Chunked content into {len(chunks)} blocks.")

    enriched_chunks = await enrich_chunks_with_llm(chunks)
    logger.info(f"Enriched {len(enriched_chunks)} chunks with LLM.")

    await store_chunks_in_db(enriched_chunks, original_name, role)
    logger.info(f"Stored chunks for '{original_name}' in database.")
    
    logger.info(f"Completed processing: {original_name}")


async def check_document_exists(document_name: str, role: str) -> bool:
    """
    Check if a document with the same name and role already exists in the database.
    Returns True if exists, else False.
    """
    db: Session = SessionLocal()
    try:
        result = db.execute(
            select(DocumentData)
            .where(DocumentData.document_name == document_name)
            .where(DocumentData.role == role)
        ).first()
        return result is not None
    except Exception as e:
        logger.error(f"Error checking document existence: {e}")
    finally:
        db.close()

async def read_file_content(file_path: str) -> str:
    """
    Reads PDF file content using PyPDF2.
    - Opens file in binary mode asynchronously.
    - Extracts and joins text from all pages.
    """
    try:
        async with aiofiles.open(file_path, 'rb') as f:
            data = await f.read()
    except Exception as e:
        logger.error(f"Error reading file.")

    try:
        reader = PyPDF2.PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logger.error(f"Error parsing PDF content: {e}")


async def chunk_content(content: str) -> list[str]:
    """
    Splits content into chunks based on character count.
    - Each chunk is between 10 and 100 characters.
    - Tries to split at sentence boundaries if possible (after '.').
    - Returns list of clean text chunks.
    """
    MIN_CHARS = 10
    MAX_CHARS = 100

    sentences = content.replace('\n', ' ').split('.') 

    chunks = []

    temp = sentences[0]
    for _,index in enumerate(sentences,1):

        if len(temp) + len(sentences[index]) < MAX_CHARS:
            temp += sentences[index] + "."
        else:
            chunks.append(temp)
            temp = sentences[index] + "."

    chunks.append(temp)

    return chunks



async def enrich_chunks_with_llm(chunks: list[str]) -> list[dict]:
    """
    Enriches each chunk with keywords and a summary using LLM.
    - Handles individual chunk failures gracefully.
    - Returns a list of dicts with: content, keywords, summary.
    """
    enriched = []

    for i, chunk in enumerate(chunks, start=1):
        try:
            llm_response = await ask_llm(
                question="Generate exactly 2 keywords per sentence in the chunk and a summary in single sentence.",
                context=chunk,
                response_format={
                    "keywords": ["k1", "k2", "k3"],
                    "summary": "one-line summary"
                }
            )
            enriched.append({
                "content": chunk,
                "keywords": ",".join(llm_response.get("keywords", [])),
                "summary": llm_response.get("summary", "")
            })
            logger.info(f"LLM enrichment done for chunk number {i}")
        except Exception as e:
            logger.error(f"LLM enrichment failed.")
            enriched.append({
                "content": chunk,
                "keywords": "",
                "summary": ""
            })

    return enriched


async def store_chunks_in_db(enriched_chunks: list[dict], document_name: str, role: str):
    """
    Stores enriched chunks into the document_data table.
    - Commits all chunks in a single transaction.
    - Handles and logs database errors.
    """
    db: Session = SessionLocal()
    try:
        db_chunks = [
            DocumentData(
                chunk_id=uuid.uuid4(),
                document_name=document_name,
                role=role,
                chunk_number=i + 1,
                chunk_content=item["content"],
                keywords=item.get("keywords", ""),
                summary=item.get("summary", "")
            )
            for i, item in enumerate(enriched_chunks)
        ]

        db.add_all(db_chunks)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Server error.")
    finally:
        db.close()
