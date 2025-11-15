import pypdf, chardet
from docx import Document

def extract_from_pdf(path:str)-> str:
    try:
        reader = pypdf.PdfReader(path)
        text =[]
        for p in reader.pages:
            t =p.extract_text() or ""
            text.append(t)

        return "\n".join(text).strip()
    except Exception:
        return ""

def extract_from_docx(path: str) -> str:
    d = Document(path)
    return "\n".join(p.text for p in d.paragraphs)

def extract_from_txt(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    enc = chardet.detect(raw).get("encoding") or "utf-8"
    return raw.decode(enc, errors="ignore")
