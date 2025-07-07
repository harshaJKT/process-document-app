from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.utils import dbquery
from app.models import DocumentData
from app.utils import chat
from app.database import SessionLocal

router = APIRouter()

def get_para(chunk_ids:list,db:Session):
    result = db.query(DocumentData.chunk_content).filter(DocumentData.chunk_id.in_(chunk_ids)).order_by(DocumentData.chunk_number).all()
    return "".join(row[0] for row in result)

def get_chunk_ids(required_keywords:list , db:Session,role:str ,required_match:int = 1)->list:

    if role != "manager":
        result = db.query(DocumentData.chunk_id, DocumentData.keywords).filter(DocumentData.role==role).all()
    else:
        result = db.query(DocumentData.chunk_id, DocumentData.keywords).all()
    related_chunk_ids = []

    for id,keywords in result:
        match_count = sum(1 for kw in keywords if kw in required_keywords)
        if match_count >= required_match:
            related_chunk_ids.append(id)
    
    return related_chunk_ids

@router.get("/retrieve")
def get_answer(question:str,role:str)->str:
    db:Session=SessionLocal()
    required_keywords = chat.get_keywords_from_ollama(question)
    chunk_ids = get_chunk_ids(required_keywords , db,role = role,required_match=1)
    if len(chunk_ids)==0:
        return "Nothng found from our side"
    para = get_para(chunk_ids,db)


    result = chat.get_answer_from_para(paragraph=para,question=question)
    return result

