import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True, encoding="utf-8-sig")


def _env(nome, padrao=None):
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    valor = valor.strip().strip('"').strip("'").strip()
    return valor or padrao


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "jobready-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'jobready.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = _env("GEMINI_API_KEY") or _env("GOOGLE_API_KEY")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
    GEMINI_MODEL_FALLBACKS = [
        m.strip()
        for m in os.environ.get(
            "GEMINI_MODEL_FALLBACKS",
            "gemini-flash-latest,gemini-3.6-flash,gemini-3.5-flash-lite",
        ).split(",")
        if m.strip()
    ]
