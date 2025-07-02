from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap
import uuid
from pydantic import BaseModel,Field

router = APIRouter()


class UserRoleCreate(BaseModel):
    user: str
    role: str


class UserRoleResponse(BaseModel):
    id: str
    user: str 
    role: str

    class Config:
        form_atttributes = True



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
        new_user_role = UserRoleMap(
            id=uuid.uuid4(),
            username=user_role.user,
            role=user_role.role
        )

        # TODO: Add to database and commit
        db.add(new_user_role)
        db.commit()
        db.refresh(new_user_role)

        response = UserRoleResponse(
            id=str(new_user_role.id),
            user=new_user_role.username,
            role=new_user_role.role,
        )
        return JSONResponse(content=response.model_dump(),status_code=201)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/user-role", response_model=list[UserRoleResponse])
def get_all_user_roles(db: Session = Depends(get_db)):
    """
    TODO: Implement GET /user-role
    - Query all user-role mappings from database
    - Return list of all mappings
    """
    try:
        # TODO: Query all UserRoleMap records
        db_users = db.query(UserRoleMap).all()
        response_users = [
            UserRoleResponse(
                id=str(user.id),
                user=user.username,
                role=user.role
            ).model_dump()
            for user in db_users
        ]
        # TODO: Convert to response format
        return JSONResponse(content=response_users)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# TODO: Implement U and D of CRUD (Create, Read implemented above, Update and Delete to be implemented)
