import uuid
import PyPDF2
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData


def divide_into_chunks(content: str, chunk_size: int = 50) -> list[str]:
    """
    Splits the content into chunks of specified size.
    Each chunk should be between 10 and 100 characters ideally.
    """
    return [
        content[i:i + chunk_size]
        for i in range(0, len(content), chunk_size)
        if 10 < len(content[i:i + chunk_size]) <= 100
    ]


async def process_document(message: dict):
    """
    Handles the document processing pipeline:
    - Reads the PDF file
    - Chunks the content
    - Stores chunks in the database
    """
    file_path = message["file_path"]
    original_name = message["original_filename"]
    role = message.get("role", "Analyst")

    print(f"[Worker] Processing file: {original_name} at {file_path}")

    # Step 1: Read PDF content
    content = await read_file_content(file_path)

    # Step 2: Split into chunks
    chunks = await chunk_content(content)

    # Step 3: Store each chunk in DB
    await store_chunks_in_db(chunks, original_name, role)

    print(f"[Worker] Completed processing: {original_name}")


async def read_file_content(file_path: str) -> str:
    """
    Extracts text content from a PDF file using PyPDF2.
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
        raise RuntimeError(f"Error reading PDF: {e}")


async def chunk_content(content: str) -> list[str]:
    """
    Splits content into chunks (between 10–100 characters). Ensures at least 4 chunks.
    """
    chunks = divide_into_chunks(content, chunk_size=50)

    if len(chunks) < 4:
        avg_len = max(10, len(content) // 4)
        chunks = [
            content[i:i + avg_len]
            for i in range(0, len(content), avg_len)
        ]

    return chunks


async def store_chunks_in_db(chunks: list[str], document_name: str, role: str):
    """
    Stores each chunk into the `document_data` table with relevant metadata.
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
        raise RuntimeError(f"Database error: {e}")
    finally:
        db.close()
