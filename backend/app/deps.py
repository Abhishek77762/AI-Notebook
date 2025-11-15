from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .auth import decode_token
from .models import User
from .db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization :str = Header(default= " "), db: Session =Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing Bearer token")

    token =   authorization.split(" ", 1)[1]
    email = decode_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user





