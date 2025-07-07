from fastapi import APIRouter, HTTPException, Query ,Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap, DocumentData
from app.ollama_utils import generate_keywords
import requests
 
router = APIRouter()
 
class RetrievalRequest(BaseModel):
    query: str
    user: str
 
@router.post("/retrieve")
def retrieve(request: RetrievalRequest, db: Session = Depends(get_db)):
    # 1. Get user role
    user_role = db.query(UserRoleMap).filter(UserRoleMap.user == request.user).first()
    if not user_role:
        raise HTTPException(status_code=403, detail="User not found or no role assigned.")
 
    # 2. Generate keywords from query
    query_keywords = generate_keywords(request.query)
    query_keywords_set = set([kw.strip().lower() for kw in query_keywords.split(",")])
 
    # 3. Fetch chunks for user's role
    chunks = db.query(DocumentData).filter(DocumentData.role == user_role.role).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="No documents for your role.")
 
    # 4. Filter chunks by keyword overlap
    filtered_chunks = []
    for chunk in chunks:
        chunk_keywords = set([kw.strip().lower() for kw in (chunk.keywords or "").split(",")])
        if query_keywords_set & chunk_keywords:
            filtered_chunks.append(chunk.chunk_content)
 
    if not filtered_chunks:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")
 
    # 5. Concatenate and ask Ollama for answer
    context = "\n".join(filtered_chunks)
    prompt = f"Answer the following question based on the provided context:\nContext:\n{context}\n\nQuestion: {request.query}"
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    answer = response.json()["response"].strip()
    return {"answer": answer}
