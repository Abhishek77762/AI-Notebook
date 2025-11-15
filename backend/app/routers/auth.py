from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from ..schemas import RegisterReq, LoginReq, GoogleAuthReq, TokenOut, MeOut
from ..models import User
from ..auth import hash_password, verify_password, create_access_token
from ..deps import get_db, get_current_user
from ..config import settings


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenOut)
def register(req: RegisterReq, db:Session =Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(409, "Email already registered")


    user=User(email=req.email, password_hash=hash_password(req.password))
    db.add(user) ; db.commit()
    token=create_access_token(user.email)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(req: LoginReq, db:Session =Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.password_hash or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token(user.email)
    return TokenOut(access_token=token)



@router.post("/google", response_model=TokenOut)
def google_login(req: GoogleAuthReq, db: Session = Depends(get_db)):
    try:
        idinfo = google_id_token.verify_oauth2_token(
            req.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        if idinfo["aud"] != settings.GOOGLE_CLIENT_ID:
            raise ValueError("Invalid audience")
        email = idinfo.get("email")
        sub = idinfo.get("sub")
        if not email or not sub:
            raise ValueError("Missing claims")
    except Exception:
        raise HTTPException(401, "Invalid Google token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, google_sub=sub, password_hash=None)
        db.add(user); db.commit()
    elif not user.google_sub:
        user.google_sub = sub
        db.commit()

    token = create_access_token(user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(email=user.email, created_at=user.created_at)