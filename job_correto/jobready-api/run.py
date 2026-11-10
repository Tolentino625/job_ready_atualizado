import os

from config import BASE_DIR

from app import create_app, db

app = create_app()

if __name__ == "__main__":
    caminho_env = os.path.join(BASE_DIR, ".env")
    chave = app.config.get("GEMINI_API_KEY")
    print(f"[JobReady] .env: {caminho_env} (existe: {os.path.exists(caminho_env)})")
    if chave:
        print(f"[JobReady] GEMINI_API_KEY carregada ({chave[:4]}...{chave[-4:]})")
    else:
        print("[JobReady] ATENCAO: GEMINI_API_KEY NAO foi carregada. "
              "Confira se o .env tem a linha GEMINI_API_KEY=sua_chave e se foi SALVO.")

    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
