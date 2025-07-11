from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DocumentData, UserRoleMap
from app.together_client import generate_keywords_and_summary, query_together_ai

router = APIRouter()

@router.get("/retrieve")
async def retrieve_answer(query: str = Query(...), user: str = Query(...), db: Session = Depends(get_db)):
    """
    Retrieve an answer based on the user's query and role.
    """

    #  Get user role
    user_record = db.query(UserRoleMap).filter(UserRoleMap.user == user).first()
    if not user_record:
        return {"error": "User not found"}

    user_role = user_record.role

    # Fetch document chunks assigned to this role
    chunks = db.query(DocumentData).filter(DocumentData.role == user_role).all()
    if not chunks:
        return {"error": "No documents available for your role"}

    # Extract keywords from the user's query using Together AI
    keywords, _ = await generate_keywords_and_summary(query)

    # Find matching chunks by comparing keywords
    matched_chunks = []
    for chunk in chunks:
        for kw in keywords.split(","):
            if kw.strip().lower() in chunk.keywords.lower():
                # both chunk content and its summary for more context
                combined = f"{chunk.chunk_content}\nSummary: {chunk.summary}"
                matched_chunks.append(combined)
                break  

    if not matched_chunks:
        return {"error": "No relevant chunks found"}

    # Merge matched chunks with summaries for better LLM response
    combined_content = "\n\n".join(matched_chunks)

    # Ask Together AI 
    answer = await query_together_ai(combined_content, query)

    return {"answer": answer}
