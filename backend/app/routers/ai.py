import os, json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from ..models import Note, Asset, User
from ..schemas import SummarizeReq, OutlineReq, SearchReq
from ..services import llm, tts,  export, rag
from ..config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/summarize")
def summarize(req: SummarizeReq, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id==req.note_id, Note.user_id==user.id).first()
    if not note: raise HTTPException(404, "Note not found")

    if req.style == "points":
        out = llm.summarize_points(note.raw_text, points=req.points, length=req.length)
    elif req.style == "paragraphs":
        out = llm.summarize_paragraphs(note.raw_text, paragraphs=req.paragraphs, length=req.length)
    else:
        raise HTTPException(400, "style must be 'points' or 'paragraphs'")
    return {"summary": out}



@router.post("/search")
def search(req: SearchReq, user: User = Depends(get_current_user)):
    hits = rag.search(user.id, req.query, top_k=req.top_k)
    answer = llm.rag_answer(req.query, hits)
    return {"answer": answer, "hits": hits}

@router.post("/podcast")
def podcast(req: OutlineReq, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id==req.note_id, Note.user_id==user.id).first()
    if not note: raise HTTPException(404, "Note not found")
    os.makedirs(settings.ASSET_DIR, exist_ok=True)
    out_path = os.path.join(settings.ASSET_DIR, f"note_{note.id}_podcast.mp3")
    tts.text_to_mp3(note.raw_text, out_path)
    asset = Asset(note_id=note.id, kind="podcast_mp3", path=out_path, meta=None)
    db.add(asset); db.commit(); db.refresh(asset)
    return {"asset_id": asset.id, "path": asset.path}



@router.post("/export/pdf")
def export_pdf(req: OutlineReq, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id==req.note_id, Note.user_id==user.id).first()
    if not note: raise HTTPException(404, "Note not found")
    out_path = os.path.join(settings.ASSET_DIR, f"note_{note.id}.pdf")
    export.export_pdf(note.raw_text, out_path)
    asset = Asset(note_id=note.id, kind="export_pdf", path=out_path)
    db.add(asset); db.commit(); db.refresh(asset)
    return {"asset_id": asset.id, "path": asset.path}
