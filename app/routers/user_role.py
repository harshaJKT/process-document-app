from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap
import uuid
from pydantic import BaseModel

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
    TODO: Implement POST /user-role
    - Create new user-role mapping
    - Generate UUID for id
    - Save to user_role_map table
    - Return created mapping
    """
    try:
        # TODO: Create new UserRoleMap instance
        new_user_role = UserRoleMap(user=user_role.user, role=user_role.role)

        # TODO: Add to database and commit
        db.add(new_user_role)
        db.commit()
        db.refresh(new_user_role)

        return UserRoleResponse(
            user=user_role.user,
            role=user_role.role,
        )
    except Exception as e:
        return {"error": str(e)}


@router.get("/user-role", response_model=list[UserRoleResponse])
def get_all_user_roles(db: Session = Depends(get_db)):
    """
    TODO: Implement GET /user-role
    - Query all user-role mappings from database
    - Return list of all mappings
    """
    try:
        # TODO: Query all UserRoleMap records

        # TODO: Convert to response format

        return []  # Placeholder
    except Exception as e:
        return {"error": str(e)}


# TODO: Implement U and D of CRUD (Create, Read implemented above, Update and Delete to be implemented)
