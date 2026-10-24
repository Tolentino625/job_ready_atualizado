# JobReady — Frontend

Aplicação **cliente independente** do JobReady: HTML, CSS e JavaScript
puro (sem framework, sem Jinja2, sem renderização no servidor). Ela roda
na sua própria porta/origem e consome a API REST do backend
(`jobready-api/`) exclusivamente via `fetch`, respeitando a separação
cliente-servidor.

## Estrutura

```
jobready-frontend/
├── index.html
├── usuarios.html
├── curriculos.html
├── perguntas.html
├── entrevistas.html
├── respostas.html
├── feedbacks.html
├── css/
│   └── style.css
└── js/
    ├── config.js   # URL base da API (API_BASE_URL)
    ├── nav.js      # Monta o menu lateral, comum a todas as páginas
    └── crud.js      # Motor genérico de telas CRUD (fetch para a API)
```

Cada página de tela chama `initCrudPage({...})` informando o recurso da
API e os campos do formulário; o `crud.js` cuida de listar, criar, editar
e excluir via `fetch`, sempre contra `API_BASE_URL` (definido em
`js/config.js`).

## Como executar

1. Suba o backend primeiro (veja o README de `jobready-api/`); por padrão
   ele fica em `http://localhost:5000`.
2. Se o backend estiver em outro endereço, ajuste `API_BASE_URL` em
   `js/config.js`.
3. Sirva esta pasta com qualquer servidor estático. Por exemplo:

```bash
cd jobready-frontend
python -m http.server 5500
```

4. Acesse **http://localhost:5500** no navegador. Você será encaminhado para `login.html`; use **Criar conta** na primeira utilização.

Como backend e frontend rodam em origens diferentes, o backend precisa
manter o CORS habilitado (já configurado com `Flask-CORS` em
`jobready-api`).
