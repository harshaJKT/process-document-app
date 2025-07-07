import uuid
import PyPDF2
import os
import asyncio
import aiofiles
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import DocumentData
from app.ollama_client import ask_ollama

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
    lines= content.split('\n')
    chunks=[]
    
    for line in lines:
        line=line.strip()
        if 10<len(line)<100:
            chunks.append(line)
        elif len(line)>=100:
            for i in range(0,len(line),100):
                part=line[i:i+100]
                if len(part)>10:
                    chunks.append(part)
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
        # Generate keywords
        keywords_prompt = (
            "Extract exactly 5 keywords from this text. "
            "Return only the keywords, separated by commas, all in lowercase, no numbering, no extra text:\n"
            f"{chunk}"
        )       
        keywords=ask_ollama(keywords_prompt).strip()

         # Generate summary
        summary_prompt = f"Summarize this text in 1 sentence. Return only the summary sentence:{chunk}"
        summary = ask_ollama(summary_prompt)

        doc_data=DocumentData(
            document_name=document_name,
            chunk_number=idx+1,
            chunk_content=chunk,
            role=role,
            keywords=keywords,
            summary=summary
        )
        db.add(doc_data)
    db.commit()
   
