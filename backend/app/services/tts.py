import os, tempfile, subprocess, shutil
import pyttsx3
from ..config import settings

def _piper_available():
    return bool(settings.PIPER_BIN and shutil.which(settings.PIPER_BIN) and settings.PIPER_VOICE and os.path.exists(settings.PIPER_VOICE))

def _piper_tts(text: str, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wav_path = out_path.replace(".mp3", ".wav")
    cmd = [
        settings.PIPER_BIN,
        "--model", settings.PIPER_VOICE,
        "--output_file", wav_path
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.communicate(text)
    if p.returncode != 0:
        raise RuntimeError("Piper failed")
    subprocess.run(["ffmpeg","-y","-i", wav_path, "-vn","-ar","44100","-ac","2","-b:a","128k", out_path], check=True)
    os.remove(wav_path)

def _pyttsx3_tts(text: str, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    wav_path = out_path.replace(".mp3", ".wav")
    engine = pyttsx3.init()
    engine.save_to_file(text, wav_path)
    engine.runAndWait()
    subprocess.run(["ffmpeg","-y","-i", wav_path, "-vn","-ar","44100","-ac","2","-b:a","128k", out_path], check=True)
    os.remove(wav_path)

def text_to_mp3(text: str, out_path: str) -> str:
    if _piper_available():
        _piper_tts(text, out_path)
    else:
        _pyttsx3_tts(text, out_path)
    return out_path
