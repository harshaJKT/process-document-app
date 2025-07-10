from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.models import UserRoleMap, DocumentData
from app.utils.llm_chat import ask_llm
from app.database import get_db
from app.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    user: str

def get_user_role(db: Session, username: str) -> str:
    """
    Fetch the role associated with a given username.
    """
    return db.scalar(
        select(UserRoleMap.role).where(UserRoleMap.username == username)
    )

async def extract_keywords(query: str) -> list[str]:
    """
    Use LLM to extract 3–5 keywords from the user's query.
    """
    response = await ask_llm(
        question="Generate exactly 3 to 5 keywords from the given question only. Do not add something else other than the words in the question.",
        context=query,
        response_format={"keywords": ["k1", "k2", "k3"]}
    )
    return response.get("keywords", [])


def filter_chunks_by_keywords(db: Session, role: str, keywords: list[str]) -> list[str]:
    """
    Filter document chunks that match any of the extracted keywords.
    """
    keyword_filters = [DocumentData.chunk_content.ilike(f"%{kw}%") for kw in keywords]
    return db.execute(
        select(DocumentData.chunk_content)
        .where(DocumentData.role == role)
        .where(or_(*keyword_filters))
    ).scalars().all()


async def get_answer(query: str, context: str) -> dict:
    """
    Use LLM to answer the query based on the provided context.
    """
    return await ask_llm(
        question=query,
        context=context,
        response_format={"answer": "The document approval process involves..."}
    )


# --- Main Endpoint ---

@router.post("/query")
async def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Handles user query on a document:
    - Retrieves user's role
    - Gets relevant document chunks for that role
    - Extracts keywords using LLM
    - Filters chunks with those keywords
    - Uses LLM to answer the query based on filtered context
    """
    
    role = get_user_role(db, request.user)
    logger.info(f"Retrieved role '{role}' for user '{request.user}'")

    keywords = await extract_keywords(request.query)
    logger.info(f"Extracted keywords: {keywords}")

    filtered_chunks = filter_chunks_by_keywords(db, role, keywords)
    logger.info(f"Filtered down to {len(filtered_chunks)} relevant chunks")

    final_context = "\n".join(filtered_chunks)
    answer = await get_answer(request.query, final_context)
    logger.info("Successfully generated answer from LLM")

    return {"response": answer}
