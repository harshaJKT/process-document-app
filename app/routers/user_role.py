from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import psycopg2
from app.models import UserRoleMap
import uuid
from pydantic import BaseModel
from fastapi import HTTPException
import config
from app.utils import dbquery

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
        new_user_role = UserRoleMap(user=user_role.user, role=user_role.role.lower())

        # TODO: Add to database and commit
        db.add(new_user_role)
        db.commit()
        db.refresh(new_user_role)

        return UserRoleResponse(
            id=str(new_user_role.id),
            user=user_role.user,
            role=user_role.role,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/user-role", response_model=list[UserRoleResponse])
def get_all_user_roles():
    """
    TODO: Implement GET /user-role
    - Query all user-role mappings from database
    - Return list of all mappings
    """
    try:
        # TODO: Query all UserRoleMap records
        dburl = config.DATABASE_URL
        table = "user_role_map"
        cols = ['id' , '"user"' , 'role']
        cols_str = ', '.join(cols)
        query = f"select {cols_str} from {table};"
        user_roles = dbquery.query_db_postgres(dburl , query)

        # TODO: Convert to response format
        #normalizing the col name as user is a keyword in postgres
        normalized_cols = [col.strip('"') for col in cols]


        result = [dict(zip(normalized_cols,row)) for row in user_roles]

        return   result# Placeholder
    except Exception as e:
        return {"error": str(e)}


# TODO: Implement U and D of CRUD (Create, Read implemented above, Update and Delete to be implemented)
