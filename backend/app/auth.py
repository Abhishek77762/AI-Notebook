from datetime import datetime ,timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException,status
from typing import Optional
from .config import  settings

ALGO = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(pw:str)->str:
    return pwd_context.hash(pw)

def verify_password(pw:str,hashed:str)->bool:
    return pwd_context.verify(pw,hashed)


def create_access_token(sub: str, expires_minutes:int |None = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub":sub , "exp" : expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGO)


def  decode_token(token:str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])
        sub: str = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return sub
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


