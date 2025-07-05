from fastapi import APIRouter, Depends, HTTPException, status
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
    try:
        new_user_role = UserRoleMap(user=user_role.user, role=user_role.role)
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
    try:
        roles = db.query(UserRoleMap).all()
        return [
            UserRoleResponse(
                id=str(role.id),
                user=role.user,
                role=role.role
            )
            for role in roles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/user-role/{id}", response_model=UserRoleResponse)
def update_user_role(id: str, updated_data: UserRoleCreate, db: Session = Depends(get_db)):
    try:
        role_entry = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
        if not role_entry:
            raise HTTPException(status_code=404, detail="User role not found")

        role_entry.user = updated_data.user
        role_entry.role = updated_data.role
        db.commit()
        db.refresh(role_entry)

        return UserRoleResponse(
            id=str(role_entry.id),
            user=role_entry.user,
            role=role_entry.role
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user-role/{id}")
def delete_user_role(id: str, db: Session = Depends(get_db)):
    try:
        role_entry = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
        if not role_entry:
            raise HTTPException(status_code=404, detail="User role not found")

        db.delete(role_entry)
        db.commit()
        return {"message": f"User role with id {id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
