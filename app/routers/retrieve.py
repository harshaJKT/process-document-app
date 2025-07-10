from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap, DocumentData
from app.llm_utils import extract_query_keywords, query_ollama
 
router = APIRouter()
 
@router.get("/retrieve")
async def retrieve_answer(query: str = Query(...), user: str = Query(...), db: Session = Depends(get_db)):
    roles = db.query(UserRoleMap.role).filter(UserRoleMap.user == user).all()
    roles = [r.role for r in roles]
    if not roles:
        raise HTTPException(status_code=403, detail="User has no access roles")
 
    print(f"[Info] User '{user}' has roles: {roles}")
 
    query_keywords = await extract_query_keywords(query)
    print(f"[Info] Query keywords: {query_keywords}")
 
    chunks = db.query(DocumentData).filter(DocumentData.role.in_(roles)).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="No accessible documents for this user")
 
    context = "\n\n".join([
        f"Chunk {c.chunk_number}:\nContent: {c.chunk_content}\nKeywords: {c.keywords}"
        for c in chunks
    ])
 
    print(f"[Info] Total context length: {len(context)}")
 
    answer = await query_ollama(query=query, context=context)
    print(f"[Info] Final LLM answer: {answer[:200]}...")
 
    return {
        "answer": answer,
        "matched_chunks": len(chunks),
        "query_keywords": query_keywords
    }