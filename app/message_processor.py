import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.chat_prompt import get_prompt
from app.database import SessionLocal
from app.models import DocumentData
from app.ollama_chatbot import OllamaChatbot  
from app.gemini_chatbot import GeminiClient


# chatbot = OllamaChatbot()
chatbot = GeminiClient()


async def process_document(message):
    """
    Process uploaded document: read, chunk, store
    """
    file_path = message["file_path"]
    original_name = message["original_name"]
    role = message.get("role_required", "Analyst")

    print(f"[Worker] Processing file: {original_name} at {file_path}")

    try:
        # Step 1: Read content
        content = await read_file_content(file_path)

        # Step 2: Chunk content
        chunks = await chunk_content(content)

        # Step 3: Store in DB
        await store_chunks_in_db(chunks, original_name, role)

        print(f"[Worker] Completed processing: {original_name}")

    except Exception as e:
        print(f"[Worker] Error processing {original_name}: {str(e)}")


async def read_file_content(file_path):
    """
    Read content from a PDF or text file
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        content = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                content += page.extract_text() or ""
        return content.strip()

    elif ext == ".txt":
        async with aiofiles.open(file_path, mode='r') as f:
            content = await f.read()
        return content.strip()

    else:
        raise ValueError("Unsupported file format. Only .pdf and .txt are allowed.")


async def chunk_content(content):
    """
    Split content into chunks of ~100 characters (min 10)
    """
    content = content.replace("\n", " ").strip()
    chunks = []
    chunk_size = 100
    min_size = 10

    index = 0
    while index < len(content):
        chunk = content[index:index + chunk_size].strip()
        if len(chunk) >= min_size:
            chunks.append(chunk)
        index += chunk_size

    if len(chunks) < 4:
        chunks += ["..."] * (4 - len(chunks))

    return chunks


async def store_chunks_in_db(chunks, document_name, role):
    """
    Save all chunks into document_data table
    """
    db: Session = SessionLocal()
    try:
        for idx, chunk in enumerate(chunks):
            keyword_prompt = get_prompt("keyword")
            summary_prompt = get_prompt("summary")
            keywords = chatbot.chat(keyword_prompt(chunk))
            summary = chatbot.chat(summary_prompt(chunk))
            record = DocumentData(
                chunk_id=uuid.uuid4(),
                document_name=document_name,
                chunk_number=idx + 1,
                chunk_content=chunk,
                keywords=keywords,
                summary=summary,
                role=role,
            )
            db.add(record)
            print(keywords, summary)
        db.commit()
        print(f"[DB] Stored {len(chunks)} chunks for {document_name}")
    except Exception as e:
        db.rollback()
        print(f"[DB] Error saving to DB: {str(e)}")
    finally:
        db.close()
