import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def export_pdf(text:str, out_path:str)->str:
    os.makedirs(os.path.dirname(out_path), exist_ok = True)
    c = canvas.Canvas(out_path, pagesize=LETTER)
    width,height = LETTER
    y= height - 72
    for line in text.splitlines() or [" "]:
        if y < 72 :
            c.showPage()
            y = height - 72
        c.drawString(54, y, line[:110])
        y -= 16
        c.save()
        return out_path
