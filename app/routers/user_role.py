from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.models import UserRoleMap
from app.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


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

        logger.info(f"Created user-role: {new_user_role.username} -> {new_user_role.role}")

        return JSONResponse(
            content=UserRoleResponse(
                id=str(new_user_role.id),
                user=new_user_role.username,
                role=new_user_role.role
            ).model_dump(),
            status_code=201
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.exception("Database error while creating user-role")
        return JSONResponse(content={"error": "Database error"}, status_code=500)
    except Exception as e:
        logger.exception("Unexpected error while creating user-role")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/user-role", response_model=list[UserRoleResponse])
def get_all_user_roles(db: Session = Depends(get_db)):
    """
    Retrieve all user-role mappings from the database.
    """
    try:
        db_users = db.query(UserRoleMap).all()
        logger.info(f"Fetched {len(db_users)} user-role records.")

        return [
            UserRoleResponse(
                id=str(user.id),
                user=user.username,
                role=user.role
            )
            for user in db_users
        ]

    except SQLAlchemyError:
        logger.exception("Database error while fetching user-roles")
        return JSONResponse(content={"error": "Database error"}, status_code=500)
    except Exception as e:
        logger.exception("Unexpected error while fetching user-roles")
        return JSONResponse(content={"error": str(e)}, status_code=500)
