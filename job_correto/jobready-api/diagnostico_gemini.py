#!/usr/bin/env python3
"""
Script de diagnóstico ISOLADO para a integração com o Gemini.

Roda uma única chamada simples ao Gemini, fora do Flask, e imprime o erro
REAL devolvido pelo Google (código HTTP + mensagem), em vez da mensagem
genérica "sobrecarregado" que a API do JobReady mostra depois de esgotar
as tentativas automáticas.

Uso:
    cd jobready-api
    export GEMINI_API_KEY="sua-chave-aqui"     # ou GOOGLE_API_KEY
    export GEMINI_MODEL="gemini-3.7-flash"     # opcional, mesmo default da API
    python3 diagnostico_gemini.py

Isso ajuda a distinguir rapidamente as causas mais comuns de falha:
- Chave inválida/não configurada          -> erro de autenticação (401/403)
- Cota/limite de uso excedido             -> HTTP 429 (RESOURCE_EXHAUSTED)
- Modelo não existe ou não está disponível-> HTTP 404 (NOT_FOUND) ou 400
- Sobrecarga passageira do serviço        -> HTTP 500/503/504
- Sem acesso à internet/rede bloqueada    -> erro de conexão (não é HTTP)
"""
import os
import sys

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
model = os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")

if not api_key:
    print("❌ GEMINI_API_KEY (ou GOOGLE_API_KEY) não está definida no ambiente atual.")
    print("   Defina com: export GEMINI_API_KEY='sua-chave-aqui'")
    sys.exit(1)

print(f"Testando modelo: {model}")
print(f"Chave começa com: {api_key[:6]}... (tamanho: {len(api_key)})")
print("-" * 60)

try:
    from google import genai
    from google.genai import types
    from google.genai import errors as genai_errors
except ImportError as exc:
    print(f"❌ Não foi possível importar o SDK google-genai: {exc}")
    print("   Instale/atualize com: pip install -U google-genai")
    sys.exit(1)

try:
    import google.genai as _g
    print(f"Versão instalada do google-genai: {getattr(_g, '__version__', 'desconhecida')}")
except Exception:
    pass

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model=model,
        contents="Responda apenas com a palavra: ok",
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=20),
    )
    print("✅ SUCESSO! O Gemini respondeu normalmente.")
    print("Resposta:", response.text)
except genai_errors.APIError as exc:
    codigo = getattr(exc, "code", None)
    status = getattr(exc, "status", None)
    detalhes = getattr(exc, "details", None) or getattr(exc, "message", None) or str(exc)
    print(f"❌ ERRO REAL do Gemini — código: {codigo} | status: {status}")
    print(f"   Detalhe: {detalhes}")
    print()
    if codigo == 429:
        print("➡️  Isso é LIMITE DE COTA/USO, não 'alta demanda temporária'.")
        print("   Verifique o uso e os limites da sua chave em:")
        print("   https://aistudio.google.com/usage")
        print(f"   Confirme também se o modelo '{model}' está disponível no seu plano/projeto.")
    elif codigo in (404, 400):
        print(f"➡️  O modelo '{model}' pode não existir ou não estar disponível para esta chave/projeto.")
        print("   Veja os modelos disponíveis em: https://ai.google.dev/gemini-api/docs/models")
    elif codigo in (401, 403):
        print("➡️  Problema de autenticação: a chave pode estar inválida, revogada ou sem permissão.")
    elif codigo in (500, 503, 504):
        print("➡️  Isso sim é sobrecarga/instabilidade real do serviço do Google. Tente de novo em alguns minutos.")
except Exception as exc:
    print(f"❌ ERRO DE CONEXÃO/OUTRO (não é um erro HTTP do Gemini): {type(exc).__name__}: {exc}")
    print("   Isso costuma indicar rede/firewall bloqueando o acesso a generativelanguage.googleapis.com,")
    print("   ou algum outro problema fora da API do Gemini em si.")
