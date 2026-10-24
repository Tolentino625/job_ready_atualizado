import os
import uuid
from pathlib import Path

from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "gif", "webp",
    "doc", "docx", "txt", "rtf", "odt", "heic"
}
MAX_FILE_SIZE = 10 * 1024 * 1024


def uploads_dir():
    path = Path(__file__).resolve().parents[3] / "uploads" / "curriculos"
    path.mkdir(parents=True, exist_ok=True)
    return path


def salvar_arquivo(arquivo):
    if not arquivo or not arquivo.filename:
        return None

    nome_seguro = secure_filename(arquivo.filename)
    if not nome_seguro or "." not in nome_seguro:
        raise ValueError("Arquivo sem extensão válida.")

    extensao = nome_seguro.rsplit(".", 1)[1].lower()
    if extensao not in ALLOWED_EXTENSIONS:
        permitidos = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Tipo de arquivo não permitido. Use: {permitidos}.")

    # O limite do Flask também protege a requisição. Esta verificação cobre
    # streams que informem o tamanho antes do salvamento.
    tamanho = getattr(arquivo, "content_length", None)
    if tamanho and tamanho > MAX_FILE_SIZE:
        raise ValueError("O arquivo deve ter no máximo 10 MB.")

    nome_final = f"{uuid.uuid4().hex}.{extensao}"
    destino = uploads_dir() / nome_final
    arquivo.save(destino)

    if destino.stat().st_size > MAX_FILE_SIZE:
        destino.unlink(missing_ok=True)
        raise ValueError("O arquivo deve ter no máximo 10 MB.")

    return {
        "nome_arquivo": nome_seguro,
        "arquivo_path": str(destino.relative_to(uploads_dir().parent.parent)),
        "arquivo_mimetype": arquivo.mimetype or "application/octet-stream",
    }


def apagar_arquivo(arquivo_path):
    if not arquivo_path:
        return
    base = uploads_dir().parent.parent
    caminho = (base / arquivo_path).resolve()
    base_resolvido = base.resolve()
    try:
        caminho.relative_to(base_resolvido)
    except ValueError:
        return
    if caminho.is_file():
        caminho.unlink(missing_ok=True)
