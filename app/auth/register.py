from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
import bcrypt

from app.database.db_depends import get_db
from app.users.models.users import Users
from app.schemas.schemas import CreateUser

router = APIRouter(prefix="/register", tags=["auth"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register(user: CreateUser, db: AsyncSession = Depends(get_db)):
    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    await db.execute(insert(Users).values(email=user.email, username=user.username, password=hashed.decode('utf-8')))
    await db.commit()
    return {"message": "registered"}
