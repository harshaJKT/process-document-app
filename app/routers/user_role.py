from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap
import uuid
from pydantic import BaseModel
from fastapi import HTTPException
 
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
    Implement POST /user-role
    - Create new user-role mapping
    - Generate UUID for id
    - Save to user_role_map table
    - Return created mapping
    """
    try:
        # Generate UUID for the new user-role mapping
        new_id = uuid.uuid4()
        # Create new UserRoleMap instance
        new_user_role = UserRoleMap(id=new_id, user=user_role.user, role=user_role.role)
        # Add to database and commit
        db.add(new_user_role)
        db.commit()
        db.refresh(new_user_role)

        return UserRoleResponse(
            id=str(new_user_role.id),
            user=new_user_role.user,
            role=new_user_role.role,
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
        user_roles = db.query(UserRoleMap).all()
        # TODO: Convert to response format
        return [UserRoleResponse(id=str(ur.id), user=ur.user, role=ur.role) for ur in user_roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
# TODO: Implement U and D of CRUD (Create, Read implemented above, Update and Delete to be implemented)


@router.put("/user-role/{id}", response_model=UserRoleResponse)
def update_user_role(
    id: str,
    updated_role: UserRoleCreate,
    db: Session = Depends(get_db)
):
    """
    Implement PUT /user-role/{id}
    - Find the mapping by ID
    - Update user and role fields
    - Save changes to database
    - Return updated mapping
    """
    try:
        # Fetch the existing user-role mapping
        user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()

        if not user_role:
            raise HTTPException(status_code=404, detail="User-Role mapping not found")

        user_role.user = updated_role.user
        user_role.role = updated_role.role

        db.commit()
        db.refresh(user_role)

        return UserRoleResponse(id=str(user_role.id), user=user_role.user, role=user_role.role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user-role/{id}", status_code=204)
def delete_user_role(id: str, db: Session = Depends(get_db)):
    """
    Implement DELETE /user-role/{id}
    - Find mapping by ID
    - Delete from database
    - Return 204 No Content
    """
    try:
        user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()

        if not user_role:
            raise HTTPException(status_code=404, detail="User-Role mapping not found")

        db.delete(user_role)
        db.commit()

        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
