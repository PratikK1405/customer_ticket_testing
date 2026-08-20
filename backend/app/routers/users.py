from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.enums import UserRole
from backend.app.schemas.user import UserRead, UserUpdate
from backend.app.crud.base import CRUDBase
from backend.app.dependencies import require_role

router = APIRouter(prefix="/users", tags=["Users"])
crud = CRUDBase(User)

@router.get("/", response_model=list[UserRead], dependencies=[Depends(require_role(UserRole.admin))])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_all(db, skip, limit)

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_role(UserRole.admin))])
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await crud.get(db, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    return obj

@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_role(UserRole.admin))])
async def update_user(user_id: UUID, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.get(db, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    return await crud.update(db, obj, payload.model_dump(exclude_unset=True))

@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_role(UserRole.admin))])
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    obj = await crud.get(db, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    await crud.delete(db, obj)