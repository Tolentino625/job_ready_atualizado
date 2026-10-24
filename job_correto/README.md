JobReady — API + CRUD (Flask)
O JobReady é um projeto para ajudar estudantes e candidatos a se prepararem para entrevistas de emprego: simulações de entrevista, feedback de desempenho, histórico, análise de currículo e banco de perguntas frequentes.

Esta entrega implementa, no backend da API, o CRUD completo das principais Models do domínio, seguindo a arquitetura Model → Service → Controller, além das telas de frontend (cadastrar, listar, editar, excluir) que consomem essas rotas de API.

1. Arquitetura
jobready-api/
├── app/
│   ├── models/          # Models (herdam de db.Model / SQLAlchemy) com métodos de CRUD
│   ├── services/        # Regras de negócio e validação, chamadas pelos Controllers
│   ├── controllers/     # Blueprints Flask: rotas de API (/api/...) e rotas de tela
│   ├── templates/       # Telas HTML (uma pasta por entidade) que chamam a API via fetch
│   ├── static/          # CSS e o motor de CRUD em JS (static/js/crud.js)
│   ├── extensions.py    # Instância do SQLAlchemy (db)
│   └── __init__.py      # App factory, registra os Blueprints
├── config.py             # Configuração (SQLite por padrão)
├── run.py                # Ponto de entrada da aplicação
├── seed.py                # Popula o banco com perguntas de exemplo (opcional)
└── requirements.txt
Fluxo de uma requisição: Controller (rota) → Service (valida os dados e aplica regra de negócio) → Model (executa a operação no banco via métodos próprios: criar, listar, buscar_por_id, atualizar, deletar).

2. Models e funcionalidades implementadas
Model	Descrição	Rotas de API
Usuario	Cadastro/login de usuários da plataforma	/api/usuarios
Curriculo	Upload e análise de currículo (arquivo, pontos fortes/fracos)	/api/curriculos
Pergunta	Banco de perguntas frequentes de entrevista, com sugestão de resposta	/api/perguntas
Entrevista	Simulações de entrevista (tipo texto/voz, status, pontuação)	/api/entrevistas
Resposta	Resposta do usuário a uma pergunta dentro de uma entrevista	/api/respostas
Feedback	Feedback de desempenho (pontuação, pontos fortes/a melhorar)	/api/feedbacks
Cada recurso acima possui as 5 rotas padrão de CRUD:

GET    /api/<recurso>          → lista todos os registros
GET    /api/<recurso>/<id>     → busca um registro por id
POST   /api/<recurso>          → cria um novo registro
PUT    /api/<recurso>/<id>     → atualiza um registro existente
DELETE /api/<recurso>/<id>     → remove um registro
3. Telas (frontend)
Cada Model tem uma tela correspondente, acessível pelo menu lateral:

/usuarios
/curriculos
/perguntas
/entrevistas
/respostas
/feedbacks
Cada tela lista os registros em uma tabela e permite criar, editar e excluir através de um modal, chamando as próprias rotas /api/... via fetch (arquivo app/static/js/crud.js) — ou seja, o frontend não acessa o banco diretamente, apenas consome a API já implementada.

4. Como executar o projeto
Pré-requisitos: Python 3.10+

# 1. Clone o repositório e entre na pasta
git clone <link-do-repositorio>
cd jobready-api

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) popule o banco com perguntas de exemplo
python seed.py

# 5. Rode a aplicação
python run.py
A aplicação sobe em http://localhost:5000. O banco (SQLite) é criado automaticamente na primeira execução (jobready.db).

5. Testando a API diretamente (exemplo com curl)
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

# Lista das 10 funcionalidades
1-Cadastrar Usuario
2-Listar Usuario 
3-Excluir Usuario 
4-Editar Usuario 
5-Cadastrar lembrete de estudo
6-Listar lembrete de estudo 
7-Excluir lembrete de estudo 
8-Editar lembrete de estudo 
9-Upload de Arquivo 
10-Editar Arquivo etc


# Novas funcionalidades
avaliação de curriculo com ia
gerar perguntas com ia
escolher area de gerar poergfuntas 
gerar avaliação das respostas das perguntas com ia
simulação de entrevista com ia 
avaliação de respostas da entrevista com ia 
feedback da entrevista com ia 


# Excluir usuário (id 1)
curl -X DELETE http://localhost:5000/api/usuarios/1
6. Integrantes do grupo
Julio Bravim
Lucas Tolentino
Arthur de Souza
Diogo Figueiredo
Joao Senna
Felipe Gabriel
