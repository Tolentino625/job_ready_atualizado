import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configurações gerais da aplicação Flask."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "jobready-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'jobready.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
    # Modelos tentados, em ordem, se o principal estiver indisponível
    # (sobrecarregado/fora do ar) ou não existir mais para esta chave.
    # "gemini-flash-latest" é um "alias" do próprio Google que aponta para
    # a versão Flash estável mais atual. Modelos da geração 2.5 (ex:
    # gemini-2.5-flash) NÃO são mais liberados para contas/chaves novas
    # (erro 404 "no longer available to new users"), então usamos apenas
    # a geração 3.x como fallback. Separe por vírgula para configurar sua
    # própria lista via variável de ambiente.
    GEMINI_MODEL_FALLBACKS = [
        m.strip()
        for m in os.environ.get(
            "GEMINI_MODEL_FALLBACKS",
            "gemini-flash-latest,gemini-3.6-flash,gemini-3.5-flash-lite",
        ).split(",")
        if m.strip()
    ]
