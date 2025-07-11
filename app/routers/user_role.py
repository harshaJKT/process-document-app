from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRoleMap
from pydantic import BaseModel
from typing import List
from uuid import UUID, uuid4

router = APIRouter()


# Request body for creating or updating user roles
class UserRoleCreate(BaseModel):
    user: str
    role: str

# Response model for returning user role data
class UserRoleResponse(BaseModel):
    id: UUID
    user: str
    role: str


@router.post("/user-role", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """Create a new user role."""
    new_user_role = UserRoleMap(id=uuid4(), user=user_role.user, role=user_role.role)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return new_user_role


@router.get("/user-role", response_model=List[UserRoleResponse])
def get_all_user_roles(db: Session = Depends(get_db)):
    """Get all user roles."""
    return db.query(UserRoleMap).all()


@router.put("/user-role/{id}", response_model=UserRoleResponse)
def update_user_role(id: UUID, updated_data: UserRoleCreate, db: Session = Depends(get_db)):
    """Update a specific user role by ID."""
    user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    user_role.user = updated_data.user
    user_role.role = updated_data.role
    db.commit()
    db.refresh(user_role)
    return user_role


@router.delete("/user-role/{id}", status_code=status.HTTP_200_OK)
def delete_user_role(id: UUID, db: Session = Depends(get_db)):
    """Delete a specific user role by ID."""
    user_role = db.query(UserRoleMap).filter(UserRoleMap.id == id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="User role not found")

    db.delete(user_role)
    db.commit()
    return {"message": f"User role {id} deleted successfully"}
