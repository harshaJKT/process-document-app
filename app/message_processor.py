import uuid
import PyPDF2
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData
from app.together_client import generate_keywords_and_summary

def divide_into_chunks(text: str, chunk_size: int = 50) -> list[str]:
    """
    Split the text into smaller parts (chunks) of a given size.
    """
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if 10 < len(chunk) <= chunk_size:
            chunks.append(chunk)
    return chunks

async def process_document(message: dict):
    """
    Function to process the document:
    1. Read the PDF file.
    2. Split the content into smaller parts.
    3. Generate keywords and summary for each part.
    4. Store everything in the database.
    """
    file_path = message["file_path"]
    document_name = message["original_filename"]
    role = message.get("role", "Default")  # Default role is 'Default'

    print(f"Processing document: {document_name}")

    print(f"Reading PDF")
    content = await read_pdf(file_path)
    print(f"PDF content read successfully ({len(content)} characters)")

    print(f"Splitting content into chunks")
    chunks = await split_content(content)
    print(f"Content split into {len(chunks)} chunks")
    
    print(f"Saving chunks to database")
    await save_chunks_to_database(chunks, document_name, role)
    print(f"Chunks saved to database successfully")

async def read_pdf(file_path: str) -> str:
   
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text.strip()

async def split_content(text: str) -> list[str]:
    """
    Split the text into chunks.
    Ensure at least 4 chunks by adjusting the size if needed.
    """
    chunks = divide_into_chunks(text)

    # If less than 4 chunks, forcefully split into 4 parts
    if len(chunks) < 4:
        part_size = max(10, len(text) // 4)
        chunks = [
            text[i:i + part_size]
            for i in range(0, len(text), part_size)
        ]

    return chunks

async def save_chunks_to_database(chunks: list[str], document_name: str, role: str):
    """
    Save each chunk along with its keywords and summary into the database.
    """
    db: Session = SessionLocal()
    try:
        for idx, chunk in enumerate(chunks):
            # Generate keywords and summary for this chunk
            keywords, summary = await generate_keywords_and_summary(chunk)

            # Create a new database record
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
        raise RuntimeError(f"Failed to save to database: {e}")
    finally:
        db.close()  
