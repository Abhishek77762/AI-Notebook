import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from ..models import Note, Asset, User
from ..schemas import NoteCreate, NoteUpdate, NoteOut
from ..config import settings
from ..services.extract import extract_from_pdf, extract_from_docx, extract_from_txt
from ..services import rag
from datetime import datetime
from typing import List

router = APIRouter(prefix="/notes", tags=["notes"])

@router.post("", response_model=NoteOut)
def create_note(payload: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = Note(user_id=user.id, title=payload.title, raw_text=payload.raw_text, html=payload.html)
    db.add(n); db.commit(); db.refresh(n)
    rag.add_note(user.id, n.id, n.raw_text)
    return n

@router.get("", response_model=List[NoteOut])
def list_notes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Note).filter(Note.user_id==user.id).order_by(Note.created_at.desc()).all()

@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.query(Note).filter(Note.id==note_id, Note.user_id==user.id).first()
    if not n: raise HTTPException(404, "Note not found")
    return n

@router.post("/upload", response_model=NoteOut)
async def upload_note(file: UploadFile = File(...), title: str = Form("Untitled"),
                      db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    os.makedirs(settings.FILE_DIR, exist_ok=True)
    dest = os.path.join(settings.FILE_DIR, file.filename)
    with open(dest, "wb") as f:
        f.write(await file.read())

    ext = (file.filename.split(".")[-1] or "").lower()
    if ext == "pdf":
        text = extract_from_pdf(dest); kind = "upload_pdf"
    elif ext in ("docx", "doc"):
        text = extract_from_docx(dest); kind = "upload_docx"
    elif ext in ("txt",):
        text = extract_from_txt(dest); kind = "upload_txt"
    else:
        raise HTTPException(400, "Unsupported file type")

    if not text: raise HTTPException(422, "Could not extract text from file")

    note = Note(user_id=user.id, title=title, raw_text=text, html=None,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(note); db.commit(); db.refresh(note)
    asset = Asset(note_id=note.id, kind=kind, path=dest)
    db.add(asset); db.commit()

    rag.add_note(user.id, note.id, note.raw_text)
    return note

@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, payload: NoteUpdate,
                db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    n = db.query(Note).filter(Note.id==note_id, Note.user_id==user.id).first()
    if not n: raise HTTPException(404, "Note not found")

    changed = False
    if payload.title is not None and payload.title != n.title:
        n.title = payload.title; changed = True
    if payload.raw_text is not None and payload.raw_text != n.raw_text:
        n.raw_text = payload.raw_text; changed = True
    if payload.html is not None and payload.html != n.html:
        n.html = payload.html; changed = True

    if changed:
        n.updated_at = datetime.utcnow()
        db.commit(); db.refresh(n)
        # Re-index RAG for this note
        rag.remove_note(user.id, n.id)
        rag.add_note(user.id, n.id, n.raw_text)

    return n
