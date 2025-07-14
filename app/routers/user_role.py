from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
import uuid
from app.database import get_db
from app.models import UserRoleMap
from app.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class UserRoleCreate(BaseModel):
    user: str
    role: str

class UserRoleResponse(BaseModel):
    id: str
    user: str
    role: str


@router.post("/user-role", response_model=UserRoleResponse, status_code=201)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """
    Create a new user-role mapping and store it in the database.
    """
    try:
        new_user_role = UserRoleMap(
            id=uuid.uuid4(),
            username=user_role.user,
            role=user_role.role
        )

        db.add(new_user_role)
        db.commit()
        db.refresh(new_user_role)

        logger.info(f"Created user-role: {new_user_role.username} => {new_user_role.role}")

        return JSONResponse(
            content=UserRoleResponse(
                id=str(new_user_role.id),
                user=new_user_role.username,
                role=new_user_role.role
            ).model_dump(),
            status_code=201
        )

    except Exception as e:
        db.rollback()
        logger.exception("Server error.")
        return JSONResponse(content={"error": "Server error"}, status_code=500)


@router.get("/user-role", response_model=list[UserRoleResponse])
def get_all_user_roles(db: Session =  Depends(get_db)):
    """
    Retrieve all user-role mappings from the database.
    """
    try:
        db_users = db.query(UserRoleMap).all()
        logger.info(f"Fetched {len(db_users)} user-role records.")
        response_array = [
            UserRoleResponse(
                id=str(user.id),
                user=user.username,
                role=user.role
            )
            for user in db_users
        ]
        return response_array

    except Exception as e:
        logger.exception("Server error .")
        return JSONResponse(content={"error": "Server error"}, status_code=500)
