from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DocumentData, UserRoleMap
from app.gemini_chatbot import GeminiClient
from app.chat_prompt import get_prompt

chatbot = GeminiClient()
router = APIRouter()

# Request body schema
class QueryRequest(BaseModel):
    query: str
    role: str

@router.post("/query")
async def query_documents(request: QueryRequest, db: Session = Depends(get_db)):
    query = request.query
    role = request.role

    # Get user role
    user_role = db.query(UserRoleMap).filter(UserRoleMap.role == role).first()
    if not user_role:
        raise HTTPException(status_code=403, detail="User not authorized")

    # Generate query keywords using LLM
    keyword_prompt = get_prompt("keyword")
    keyword_response = chatbot.chat(keyword_prompt(query))
    query_keywords = set(map(str.strip, keyword_response.split(",")))

    # Fetch matching chunks based on role
    chunks = db.query(DocumentData).filter(DocumentData.role == user_role.role).all()

    # Filter chunks by keyword match
    filtered_chunks = [
        chunk.chunk_content for chunk in chunks
        if query_keywords & set(map(str.strip, (chunk.keywords or "").split(",")))
    ]

    if not filtered_chunks:
        raise HTTPException(status_code=404, detail="No relevant data found")

    # Get answer using filtered context
    combined_text = "\n".join(filtered_chunks)
    final_prompt = f"Answer the following question based on this content:\n\n{combined_text}\n\nQuestion: {query}"
    answer = chatbot.chat(final_prompt)

    return {"answer": answer}
