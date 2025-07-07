import uuid
import PyPDF2
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData
from app.together_client import generate_keywords_and_summary

def divide_into_chunks(content: str, chunk_size: int = 50) -> list[str]:
    """Splits the content into chunks of specified size."""
    return [
        content[i:i + chunk_size]
        for i in range(0, len(content), chunk_size)
        if 10 < len(content[i:i + chunk_size]) <= 100
    ]

async def process_document(message: dict):
    """Handles the document processing pipeline."""
    file_path = message["file_path"]
    original_name = message["original_filename"]
    role = message.get("role", "Analyst")

    print(f"[Worker] Processing file: {original_name} at {file_path}")

    print("[DEBUG] Reading file content...")
    content = await read_file_content(file_path)
    print("[DEBUG] Completed reading content.")

    print("[DEBUG] Chunking content...")
    chunks = await chunk_content(content)
    print(f"[DEBUG] Created {len(chunks)} chunks.")

    print("[DEBUG] Storing chunks to DB...")
    await store_chunks_in_db(chunks, original_name, role)
    print("[DEBUG] Stored chunks successfully.")

async def read_file_content(file_path: str) -> str:
    """Extracts text content from a PDF file using PyPDF2."""
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
        raise RuntimeError(f"Error reading PDF: {e}")

async def chunk_content(content: str) -> list[str]:
    """Splits content into chunks (between 10–100 characters). Ensures at least 4 chunks."""
    chunks = divide_into_chunks(content, chunk_size=50)

    if len(chunks) < 4:
        avg_len = max(10, len(content) // 4)
        chunks = [
            content[i:i + avg_len]
            for i in range(0, len(content), avg_len)
        ]

    return chunks

async def store_chunks_in_db(chunks: list[str], document_name: str, role: str):
    """Stores each chunk into the `document_data` table with keywords & summary."""
    db: Session = SessionLocal()
    try:
        for idx, chunk in enumerate(chunks):
            print(f"[DEBUG] Generating keywords & summary for chunk {idx+1}...")
            keywords, summary = await generate_keywords_and_summary(chunk)
            print(f"[DEBUG] Got keywords and summary for chunk {idx+1}.")

            record = DocumentData(
                chunk_id=str(uuid.uuid4()),
                document_name=document_name,
                chunk_number=idx + 1,
                chunk_content=chunk,
                role=role,
                keywords=keywords,
                summary=summary
            )
            db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Database error: {e}")
    finally:
        db.close()
