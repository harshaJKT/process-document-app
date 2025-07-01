from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import psycopg2
from app.models import UserRoleMap
import uuid
from pydantic import BaseModel
from fastapi import HTTPException
import config

router = APIRouter()

def query_db_postgres(dburl:str , table , columns:list):
    try:
        conn = psycopg2.connect(dburl)
        cursor = conn.cursor()

        cols_str = ', '.join(columns)
        query = f"select {cols_str} from {table};"

        cursor.execute(query)

        rows = cursor.fetchall()
        print(rows)
        return rows
    except Exception as e:
        print("Error querying db for user roles ")
        return []
    finally:
        cursor.close()
        conn.close()



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
            id=str(new_user_role.id),
            user=user_role.user,
            role=user_role.role,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/user-role", response_model=list[UserRoleResponse])
def get_all_user_roles(db: Session = Depends(get_db)):
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
        user_roles = query_db_postgres(dburl , table , cols)

        # TODO: Convert to response format
        #normalizing the col name as user is a keyword in postgres
        normalized_cols = [col.strip('"') for col in cols]


        result = [dict(zip(normalized_cols,row)) for row in user_roles]

        return   result# Placeholder
    except Exception as e:
        return {"error": str(e)}


# TODO: Implement U and D of CRUD (Create, Read implemented above, Update and Delete to be implemented)
