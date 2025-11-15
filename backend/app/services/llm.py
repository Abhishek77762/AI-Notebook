import google.generativeai as genai
from ..config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
_MODEL = "gemini-2.5-flash"

def summarize_points(text: str, points: int = 7, length : str = "medium")->str:
    prompt = f"""You are a precise note summarizer. Output only {points} bullet points.
    Keep facts and numbers accurate. Length preference: {length}.
    Text:
    {text}"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(prompt)
    return resp.text or ""


def summarize_paragraphs(text: str, paragraphs: int = 3, length: str = "medium") -> str:
    prompt = f"""Summarize the following into {paragraphs} well-structured paragraphs.
Keep terminology and numbers accurate. Length preference: {length}.
Text:
{text}"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(prompt)
    return resp.text or ""

def make_outline(text: str) -> dict:
    prompt = f"""Extract a teaching outline for slides.
Return JSON strictly matching: {{"slides":[{{"title":"string","bullets":["string","..."]}}]}}
Text:
{text}"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(prompt)
    import json
    try:
        return json.loads(resp.text)
    except Exception:
        # graceful fallback: one slide
        return {"slides": [{"title": "Overview", "bullets": ["No structured outline produced."]}]}



def rag_answer(query: str, contexts: list[dict], max_chars: int = 4500) -> str:
    """contexts: [{'text': str, 'note_id': int, 'idx': int, 'score': float}]"""
    # Trim total context
    buf, used = "", []
    for c in contexts:
        t = c["text"]
        if len(buf) + len(t) + 200 > max_chars:
            break
        used.append(c)
        buf += f"\n[Note {c['note_id']} / Chunk {c['idx']} / Score {c['score']:.3f}]\n{t}\n"
    prompt = f"""Answer the user question using ONLY the provided context snippets.
If not answerable from context, say "I don't have that in the notes."
Cite snippets inline like [note_id:chunk_idx].

Question: {query}

Context:
{buf}
"""
    model = genai.GenerativeModel(_MODEL)
    resp = model.generate_content(prompt)
    return resp.text or ""

