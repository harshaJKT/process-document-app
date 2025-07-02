from fastapi import APIRouter, Depends, HTTPException
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


class UserRoleUpdate(BaseModel):
    role: str


@router.post("/user-role", response_model=UserRoleResponse, status_code=201)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """
    Create new user-role mapping
    """
    try:
        new_user_role = UserRoleMap(
            id=str(uuid.uuid4()),
            user=user_role.user,
            role=user_role.role,
        )
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
    Get all user-role mappings
    """
    try:
        roles = db.query(UserRoleMap).all()
        return [UserRoleResponse(id=str(r.id), user=r.user, role=r.role) for r in roles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user-role/{id}", response_model=UserRoleResponse)
def update_user_role(id: str, updated_data: UserRoleUpdate, db: Session = Depends(get_db)):
    """
    Update role for a specific user-role mapping
    """
    user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="UserRoleMap not found")

    user_role.role = updated_data.role
    db.commit()
    db.refresh(user_role)

    return UserRoleResponse(id=str(user_role.id), user=user_role.user, role=user_role.role)


@router.delete("/user-role/{id}")
def delete_user_role(id: str, db: Session = Depends(get_db)):
    """
    Delete a user-role mapping
    """
    user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="UserRoleMap not found")

    db.delete(user_role)
    db.commit()
    return {"detail": f"UserRoleMap with ID {id} deleted successfully."}
