/**
 * Configuração do frontend do JobReady.
 *
 * O frontend é uma aplicação cliente totalmente independente do backend:
 * roda no seu próprio servidor/porta (ex: http://localhost:5500) e apenas
 * consome a API REST do Flask (ex: http://localhost:5000) via fetch/JSON.
 * Não há Jinja2, render_template nem HTML gerado no servidor — toda a
 * renderização das telas acontece aqui, no navegador.
 *
 * Se o backend estiver rodando em outro endereço/porta, basta ajustar a
 * constante abaixo.
 */
const API_BASE_URL = "http://localhost:5000";
