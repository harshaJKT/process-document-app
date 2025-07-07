from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DocumentData, UserRoleMap
from app.together_client import generate_keywords_and_summary, query_together_ai

router = APIRouter()

@router.get("/retrieve")
async def retrieve_answer(query: str = Query(...), user: str = Query(...), db: Session = Depends(get_db)):
    #  Get user's role
    user_record = db.query(UserRoleMap).filter(UserRoleMap.user == user).first()
    if not user_record:
        return {"error": "User not found"}

    user_role = user_record.role

    #  Fetch chunks for user's role
    chunks = db.query(DocumentData).filter(DocumentData.role == user_role).all()
    if not chunks:
        return {"error": "No documents available for your role"}

    #  Generate keywords from query
    keywords, _ = await generate_keywords_and_summary(query)

    #  Filter chunks based on keywords
    matched_chunks = [
        chunk.chunk_content
        for chunk in chunks
        if any(kw.strip().lower() in chunk.keywords.lower() for kw in keywords.split(","))
    ]

    if not matched_chunks:
        return {"error": "No relevant chunks found"}

    #  Prepare combined content for Together AI answer
    combined_content = "\n\n".join(matched_chunks)

    #  Query Together AI to get the answer
    answer = await query_together_ai(combined_content, query)
    return {"answer": answer}
