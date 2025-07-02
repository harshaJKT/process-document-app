from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.models import UserRoleMap, DocumentData
from app.utils.llm_chat import ask_llm
from app.database import get_db 
import json

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    user: str
    document_name: str


@router.post("/query")
async def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    # 1. Check user role
    user_role = db.scalar(
        select(UserRoleMap.role).where(UserRoleMap.username == request.user)
    )
    if not user_role:
        raise HTTPException(status_code=403, detail="User role not found")

    # 2. Get relevant document chunks for the given document_name and user's role
    chunks = db.execute(
        select(DocumentData.chunk_content)
        .where(DocumentData.document_name == request.document_name)
        .where(DocumentData.role == user_role)
    ).scalars().all()

    if not chunks:
        raise HTTPException(status_code=404, detail="No document chunks found for user role")

    all_context = "\n".join(chunks)

    # 3. Ask LLM to generate keywords from the user query
    keyword_response = ask_llm(
        question="Generate exactly 3 to 5 keywords from the given question only. Do not add something else other than the words in the question.",
        context=request.query,
        response_format={"keywords": ["k1", "k2", "k3"]}
    )

    keywords = keyword_response.get("keywords", [])
    if not keywords:
        raise HTTPException(status_code=500, detail="Keyword extraction failed")

    # 4. Filter document chunks again based on keywords
    keyword_filters = [DocumentData.chunk_content.ilike(f"%{kw}%") for kw in keywords]

    filtered_chunks = db.execute(
        select(DocumentData.chunk_content)
        .where(DocumentData.document_name == request.document_name)
        .where(DocumentData.role == user_role)
        .where(or_(*keyword_filters))
    ).scalars().all()

    if not filtered_chunks:
        raise HTTPException(status_code=404, detail="No matching chunks found for keywords")

    final_context = " ".join(filtered_chunks)

    # 5. Ask LLM to answer the query using the final context
    answer_response = ask_llm(
        question=request.query,
        context=final_context,
        response_format={"answer": "The document approval process involves..."}
    )

    return {"response": answer_response}
