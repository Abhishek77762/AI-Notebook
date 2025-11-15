import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from ..models import Asset, Note, User

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/{asset_id}")
def download(asset_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Asset).filter(Asset.id==asset_id).first()
    if not a: raise HTTPException(404, "Asset not found")
    note = db.query(Note).filter(Note.id==a.note_id).first()
    if not note or note.user_id != user.id:
        raise HTTPException(403, "Forbidden")
    if not os.path.exists(a.path):
        raise HTTPException(404, "File not found")
    return FileResponse(a.path, filename=os.path.basename(a.path))

