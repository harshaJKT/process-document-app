from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap
from pydantic import BaseModel
from typing import List
from uuid import UUID, uuid4

router = APIRouter()


class UserRoleCreate(BaseModel):
    user: str
    role: str


class UserRoleResponse(BaseModel):
    id: UUID  # Directly use UUID type
    user: str
    role: str


@router.post("/user-role", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    new_user_role = UserRoleMap(
        id=uuid4(),  # Generate UUID
        user=user_role.user,
        role=user_role.role
    )
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)

    return UserRoleResponse(
        id=new_user_role.id,
        user=new_user_role.user,
        role=new_user_role.role,
    )


@router.get("/user-role", response_model=List[UserRoleResponse])
def get_all_user_roles(db: Session = Depends(get_db)):
    roles = db.query(UserRoleMap).all()
    return [
        UserRoleResponse(
            id=role.id,
            user=role.user,
            role=role.role
        ) for role in roles
    ]


@router.put("/user-role/{id}", response_model=UserRoleResponse)
def update_user_role(id: UUID, updated_data: UserRoleCreate, db: Session = Depends(get_db)):
    user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    user_role.user = updated_data.user
    user_role.role = updated_data.role
    db.commit()
    db.refresh(user_role)

    return UserRoleResponse(
        id=user_role.id,
        user=user_role.user,
        role=user_role.role,
    )


@router.delete("/user-role/{id}", status_code=status.HTTP_200_OK)
def delete_user_role(id: UUID, db: Session = Depends(get_db)):
    user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    db.delete(user_role)
    db.commit()
    return {"message": f"User role {id} deleted successfully"}
