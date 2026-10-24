# JobReady — API (Flask)

O **JobReady** é um projeto para ajudar estudantes e candidatos a se
prepararem para entrevistas de emprego: simulações de entrevista, feedback
de desempenho, histórico, análise de currículo e banco de perguntas
frequentes.

Este repositório contém **apenas o backend**: uma API REST em Flask,
seguindo a arquitetura **Model → Service → Controller**. O frontend é uma
aplicação cliente **independente** (ver pasta `jobready-frontend/`, ao lado
desta), que consome esta API via HTTP/JSON — o backend não renderiza
nenhuma tela nem usa Jinja2/`render_template`.

---

## 1. Arquitetura

```
jobready-api/
├── app/
│   ├── models/          # Models (SQLAlchemy) com métodos de CRUD
│   ├── services/         # Um pacote por entidade; um arquivo .py por
│   │                     # caso de uso (ex.: criar_usuario_service.py),
│   │                     # cada um com uma classe que expõe execute()
│   ├── controllers/      # Blueprints Flask com Controllers em classe
│   │                     # (flask.views.MethodView), expondo só /api/...
│   ├── extensions.py     # Instância do SQLAlchemy (db)
│   └── __init__.py       # App factory, registra os Blueprints
├── config.py              # Configuração (SQLite por padrão)
├── run.py                 # Ponto de entrada da aplicação
├── seed.py                 # Popula o banco com perguntas de exemplo (opcional)
└── requirements.txt
```

Fluxo de uma requisição:

**Controller (classe, uma por recurso)** recebe a requisição HTTP →
instancia o **Service do caso de uso correspondente** (ex.:
`CriarUsuarioService(dados)`) e chama `.execute()` → o Service valida os
dados e aciona os métodos próprios do **Model** (`criar`, `listar`,
`buscar_por_id`, `atualizar`, `deletar`) → o Controller devolve a resposta
em JSON.

### Services — um caso de uso por classe

Cada operação de CRUD de cada entidade é uma classe própria, em seu
próprio arquivo, com um método `execute()`:

```
app/services/usuario/
├── criar_usuario_service.py       → class CriarUsuarioService
├── listar_usuarios_service.py     → class ListarUsuariosService
├── buscar_usuario_service.py      → class BuscarUsuarioService
├── atualizar_usuario_service.py   → class AtualizarUsuarioService
└── deletar_usuario_service.py     → class DeletarUsuarioService
```

O mesmo padrão se repete para `curriculo/`, `pergunta/`, `entrevista/`,
`resposta/` e `feedback/`.

Exemplo de uso dentro de um Controller:

```python
usuario = CriarUsuarioService(request.get_json(force=True)).execute()
```

### Controllers — classes (MethodView)

Cada recurso tem duas classes: uma para a coleção (`GET` lista / `POST`
cria) e outra para o item (`GET`/`PUT`/`DELETE` por id):

```python
class UsuarioListController(MethodView):
    def get(self): ...
    def post(self): ...

class UsuarioDetailController(MethodView):
    def get(self, usuario_id): ...
    def put(self, usuario_id): ...
    def delete(self, usuario_id): ...
```

## 2. Models e rotas de API

| Model        | Descrição                                                          | Rotas de API           |
|--------------|----------------------------------------------------------------------|-------------------------|
| `Usuario`    | Cadastro/login de usuários da plataforma                            | `/api/usuarios`         |
| `Curriculo`  | Upload e análise de currículo (arquivo, pontos fortes/fracos)       | `/api/curriculos`       |
| `Pergunta`   | Banco de perguntas frequentes de entrevista, com sugestão de resposta | `/api/perguntas`      |
| `Entrevista` | Simulações de entrevista (tipo texto/voz, status, pontuação)        | `/api/entrevistas`      |
| `Resposta`   | Resposta do usuário a uma pergunta dentro de uma entrevista         | `/api/respostas`        |
| `Feedback`   | Feedback de desempenho (pontuação, pontos fortes/a melhorar)        | `/api/feedbacks`        |

Cada recurso possui as 5 rotas padrão de CRUD:

```
GET    /api/<recurso>          → lista todos os registros
GET    /api/<recurso>/<id>     → busca um registro por id
POST   /api/<recurso>          → cria um novo registro
PUT    /api/<recurso>/<id>     → atualiza um registro existente
DELETE /api/<recurso>/<id>     → remove um registro
```

Esta API não possui rotas de tela nem gera HTML — o `Flask-CORS` está
habilitado para liberar o acesso ao frontend, que roda em outra
origem/porta.

## 3. Como executar o backend

Pré-requisitos: Python 3.10+

```bash
cd jobready-api

# 1. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. (Opcional) popule o banco com perguntas de exemplo
python seed.py

# 4. Rode a aplicação
python run.py
```

A API sobe em **http://localhost:5000**. O banco (SQLite) é criado
automaticamente na primeira execução (`jobready.db`).

## 4. Frontend

O frontend (telas de cadastrar/listar/editar/excluir cada entidade) vive
num projeto separado, `jobready-frontend/`, que é uma aplicação
100% client-side (HTML/CSS/JS puro, sem Jinja2) e consome esta API via
`fetch`. Veja o `README.md` daquele projeto para instruções de execução.

## 5. Testando a API diretamente (exemplo com curl)

```bash
# Criar usuário
curl -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nome": "Maria Silva", "email": "maria@email.com", "senha": "123456"}'

# Listar usuários
curl http://localhost:5000/api/usuarios

# Atualizar usuário (id 1)
curl -X PUT http://localhost:5000/api/usuarios/1 \
  -H "Content-Type: application/json" \
  -d '{"nome": "Maria S. Oliveira"}'

# Excluir usuário (id 1)
curl -X DELETE http://localhost:5000/api/usuarios/1
```

## 6. Integrantes do grupo

- Julio Bravim
- Lucas Tolentino
- Arthur de Souza
- Diogo Figueiredo
- Joao Senna
- Felipe Gabriel


## 7. Autenticação e anexos

O projeto agora possui autenticação por token: `POST /api/auth/registro`, `POST /api/auth/login`, `GET /api/auth/me` e `POST /api/auth/logout`. As rotas de CRUD exigem `Authorization: Bearer <token>`.

Currículos aceitam upload multipart no campo `arquivo`. São permitidos PDF, imagens e documentos comuns (`pdf`, `png`, `jpg`, `jpeg`, `gif`, `webp`, `doc`, `docx`, `txt`, `rtf`, `odt`), com limite de 10 MB. Os arquivos ficam em `uploads/curriculos/` e podem ser visualizados pela rota autenticada `/api/curriculos/<id>/arquivo`.

No frontend, a tela `login.html` permite entrar ou criar uma conta. As demais páginas exigem sessão e exibem a opção **Sair** no menu lateral.


## Gemini

A página de Perguntas possui o botão “Gerar perguntas com IA”. A API usa o SDK oficial `google-genai` e a variável `GEMINI_API_KEY`.

1. Copie `.env.example` para `.env`.
2. Preencha `GEMINI_API_KEY` com sua chave do Google AI Studio.
3. Instale as dependências com `pip install -r requirements.txt`.
4. Inicie a API com `python run.py`.

A chave não deve ser colocada no JavaScript do frontend nem versionada no Git.
