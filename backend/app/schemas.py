from pydantic import BaseModel, EmailStr
from datetime import datetime

# Notes
class NoteCreate(BaseModel):
    title: str
    raw_text: str
    html: str | None = None

class NoteUpdate(BaseModel):
    title: str | None = None
    raw_text: str | None = None
    html: str | None = None

class NoteOut(BaseModel):
    id: int
    title: str
    raw_text: str
    html: str | None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# AI
class SummarizeReq(BaseModel):
    note_id: int
    style: str
    length: str = "medium"
    points: int = 7
    paragraphs: int = 3

class OutlineReq(BaseModel):
    note_id: int

class SearchReq(BaseModel):
    query: str
    top_k: int = 5

# Auth
class RegisterReq(BaseModel):
    email: EmailStr
    password: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthReq(BaseModel):
    id_token: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeOut(BaseModel):
    email: EmailStr
    created_at: datetime
