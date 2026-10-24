"""
Cliente compartilhado para chamadas ao Gemini.

Centraliza aqui a criação do client, o retry com backoff exponencial para
erros transitórios (ex: 503 "model overloaded"), o fallback automático para
um modelo alternativo quando o principal continua indisponível, e a
extração de JSON da resposta - para não duplicar essa lógica em cada
service que usa IA (geração de perguntas, avaliação de currículo, etc).
"""
import json
import re
import time

from flask import current_app
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

RETRYABLE_STATUS_CODES = {429, 500, 503, 504}
MAX_TENTATIVAS = 2
ESPERA_BASE_SEGUNDOS = 2  # 2s, 4s... (backoff exponencial, por modelo)


class GeminiIndisponivelError(RuntimeError):
    """O Gemini continuou indisponível mesmo após as tentativas automáticas
    (em todos os modelos configurados, principal e fallback)."""


class GeminiCotaExcedidaError(RuntimeError):
    """A chave de API atingiu o limite de uso/cota (HTTP 429) em todos os
    modelos tentados. Isso NÃO é o mesmo que o serviço estar sobrecarregado:
    tentar de novo não resolve até a cota ser liberada (por minuto, por dia,
    ou por upgrade de plano).
    """


def obter_client():
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada no ambiente do servidor.")
    return genai.Client(api_key=api_key)


def _detalhe_erro(exc):
    status = getattr(exc, "status", None)
    detalhes = getattr(exc, "details", None) or getattr(exc, "message", None) or str(exc)
    return f"{status or ''} {detalhes}".strip()


def _tentar_modelo(client, model, contents, temperature, max_output_tokens):
    """Tenta gerar conteúdo em UM modelo, com retry e backoff exponencial.
    Em falha definitiva, relança a exceção original do SDK para quem chamou
    decidir se tenta outro modelo."""
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )
        except genai_errors.APIError as exc:
            codigo = getattr(exc, "code", None)
            ultimo_erro = exc

            if codigo not in RETRYABLE_STATUS_CODES:
                raise
            if tentativa == MAX_TENTATIVAS:
                raise

            espera = ESPERA_BASE_SEGUNDOS * (2 ** (tentativa - 1))
            current_app.logger.warning(
                "Gemini respondeu %s (tentativa %s/%s) ao chamar modelo '%s'. "
                "Detalhe: %s. Aguardando %ss antes de tentar novamente.",
                codigo, tentativa, MAX_TENTATIVAS, model, _detalhe_erro(exc), espera,
            )
            time.sleep(espera)

    raise ultimo_erro


def gerar_conteudo(contents, temperature=0.7, max_output_tokens=3000, model=None):
    """Chama client.models.generate_content com retry automático e, se o
    modelo principal continuar indisponível (ou não existir mais para esta
    chave), tenta os modelos de fallback (GEMINI_MODEL_FALLBACKS) em ordem
    antes de desistir de vez."""
    client = obter_client()
    modelo_principal = model or current_app.config.get("GEMINI_MODEL", "gemini-3.7-flash")
    fallbacks = current_app.config.get("GEMINI_MODEL_FALLBACKS", []) or []

    # Monta a lista de modelos a tentar, na ordem, sem repetir o principal
    # caso ele também apareça na lista de fallback.
    modelos = [modelo_principal]
    for fb in fallbacks:
        if fb and fb not in modelos:
            modelos.append(fb)

    ultimo_erro = None
    ultimo_modelo = None
    for indice, modelo_atual in enumerate(modelos):
        try:
            if indice > 0:
                current_app.logger.warning(
                    "Modelo principal '%s' indisponível. Tentando modelo de fallback '%s'.",
                    ultimo_modelo, modelo_atual,
                )
            return _tentar_modelo(client, modelo_atual, contents, temperature, max_output_tokens)
        except genai_errors.APIError as exc:
            ultimo_erro = exc
            ultimo_modelo = modelo_atual
            continue

    codigo = getattr(ultimo_erro, "code", None)
    detalhe = _detalhe_erro(ultimo_erro)
    modelos_tentados = " e ".join(f"'{m}'" for m in modelos)

    if codigo == 429:
        raise GeminiCotaExcedidaError(
            f"A chave de API do Gemini atingiu o limite de uso/cota (HTTP 429) "
            f"nos modelos {modelos_tentados}. Isso é diferente de 'sobrecarga "
            "temporária': tentar de novo não resolve até a cota ser liberada. "
            "Verifique o uso e os limites da chave em "
            "https://aistudio.google.com/usage. "
            f"Detalhe original do Google: {detalhe}"
        ) from ultimo_erro

    if codigo in RETRYABLE_STATUS_CODES:
        raise GeminiIndisponivelError(
            f"O serviço do Gemini respondeu com erro {codigo} mesmo após "
            f"{MAX_TENTATIVAS} tentativas automáticas em cada um dos modelos "
            f"{modelos_tentados}. Isso costuma ser instabilidade temporária "
            "do lado do Google - tente novamente em alguns minutos. "
            f"Detalhe original do Google: {detalhe}"
        ) from ultimo_erro

    raise RuntimeError(
        f"Erro ao chamar o Gemini (modelo '{ultimo_modelo}'): {detalhe}"
    ) from ultimo_erro


def extrair_json(texto):
    """Remove eventuais cercas de markdown (```json ... ```) e faz o parse."""
    texto = (texto or "").strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.IGNORECASE)
    return json.loads(texto)
