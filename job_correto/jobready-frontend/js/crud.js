/**
 * Motor genérico de telas CRUD do JobReady (frontend independente).
 *
 * Cada página (ex: usuarios.html) define um objeto de configuração com o
 * recurso da API e os campos do formulário, e chama initCrudPage().
 *
 * Todas as chamadas usam fetch() contra API_BASE_URL (definido em
 * js/config.js) — este frontend não acessa o banco de dados nem gera HTML
 * no servidor; ele apenas consome a API REST já implementada no backend.
 */

function initCrudPage(config) {
  // state.items = TODOS os itens vindos da API (o backend nunca filtra por
  // categoria/tipo). state.destacarIds guarda ids que devem aparecer
  // realçados na tabela por alguns segundos (ex: perguntas recém-geradas
  // pela IA), só para deixar claro ao usuário o que é novo e o que já
  // existia antes na lista completa.
  const state = { items: [], editingId: null, destacarIds: new Set(), filtro: {} };
  const apiUrl = `${API_BASE_URL}${config.resourcePath}`;

  const tableBody = document.querySelector("#crud-table tbody");
  const emptyState = document.querySelector("#empty-state");
  const modalBackdrop = document.querySelector("#crud-modal-backdrop");
  const modalTitle = document.querySelector("#crud-modal-title");
  const form = document.querySelector("#crud-form");
  const alertBox = document.querySelector("#crud-alert");
  const btnNovo = document.querySelector("#btn-novo");
  const btnCancelar = document.querySelector("#btn-cancelar");

  function showAlert(msg, type = "error") {
    alertBox.textContent = msg;
    alertBox.className = `alert alert-${type === "error" ? "error" : "success"}`;
    alertBox.style.display = "block";
    setTimeout(() => {
      alertBox.style.display = "none";
    }, 4000);
  }

  function itemPassaNoFiltro(item) {
    return Object.entries(state.filtro).every(([campo, valor]) => {
      if (!valor) return true;
      return String(item[campo] ?? "") === String(valor);
    });
  }

  function renderRow(item) {
    const tr = document.createElement("tr");
    if (state.destacarIds.has(item.id)) tr.classList.add("row-destaque");
    const cells = config.columns
      .map((col) => {
        const value = col.render ? col.render(item) : item[col.key] ?? "—";
        return `<td>${value}</td>`;
      })
      .join("");
    // somenteLeitura: tela só de consulta (sem Editar/Excluir; o "+ Novo" é
    // simplesmente omitido no HTML da página). semEditar: esconde só o "Editar".
    const acoes = config.somenteLeitura
      ? ""
      : `<td class="actions-cell">
        ${config.extraActions ? config.extraActions(item) : ""}
        ${config.semEditar ? "" : `<button class="btn btn-secondary btn-sm" data-action="edit" data-id="${item.id}">Editar</button>`}
        <button class="btn btn-danger btn-sm" data-action="delete" data-id="${item.id}">Excluir</button>
      </td>`;
    tr.innerHTML = `${cells}${acoes}`;
    return tr;
  }

  function renderizarTabela() {
    const visiveis = state.items.filter(itemPassaNoFiltro);
    tableBody.innerHTML = "";
    if (visiveis.length === 0) {
      emptyState.style.display = "block";
    } else {
      emptyState.style.display = "none";
      visiveis.forEach((item) => tableBody.appendChild(renderRow(item)));
    }
  }

  async function carregarLista() {
    try {
      const res = await fetch(apiUrl, { headers: authHeaders() });
      if (res.status === 401) { limparSessao(); window.location.replace("login.html"); return; }
      state.items = await res.json();
      renderizarTabela();
    } catch (err) {
      showAlert(`Não foi possível conectar à API em ${API_BASE_URL}.`);
    }
  }

  // Aplica um filtro client-side (ex: { categoria: "tecnica" }). Passe {}
  // para limpar. A tabela SEMPRE reflete o que existe no banco — isso só
  // muda o que é exibido, não o que a API retorna.
  function setFiltro(filtro) {
    state.filtro = filtro || {};
    renderizarTabela();
  }

  // Marca ids para aparecerem destacados (ex: perguntas recém-geradas pela
  // IA) por alguns segundos, e opcionalmente reaplica o filtro para que
  // essas linhas fiquem visíveis mesmo com filtro ativo.
  function destacarTemporario(ids, { limparFiltro = false } = {}) {
    if (limparFiltro) state.filtro = {};
    state.destacarIds = new Set(ids);
    renderizarTabela();
    setTimeout(() => {
      state.destacarIds = new Set();
      renderizarTabela();
    }, 6000);
  }

  function abrirModal(item = null) {
    state.editingId = item ? item.id : null;
    modalTitle.textContent = item ? `Editar ${config.singular}` : `Novo ${config.singular}`;
    form.reset();
    if (item) {
      config.fields.forEach((f) => {
        const el = form.elements[f.name];
        if (el) el.value = item[f.name] ?? "";
      });
    }
    modalBackdrop.classList.add("open");
  }

  function fecharModal() {
    modalBackdrop.classList.remove("open");
    state.editingId = null;
  }

  async function salvar(event) {
    event.preventDefault();
    const dados = {};
    config.fields.forEach((f) => {
      const el = form.elements[f.name];
      let value = el.value;
      if (f.type === "number" && value !== "") value = Number(value);
      if (value !== "") dados[f.name] = value;
    });

    const editing = state.editingId !== null;
    const url = editing ? `${apiUrl}/${state.editingId}` : apiUrl;
    const method = editing ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(dados),
      });
      if (res.status === 401) { limparSessao(); window.location.replace("login.html"); return; }
      const payload = await res.json();

      if (!res.ok) {
        showAlert(payload.erro || "Não foi possível salvar.");
        return;
      }
      showAlert(
        editing ? `${config.singular} atualizado com sucesso.` : `${config.singular} criado com sucesso.`,
        "success"
      );
      fecharModal();
      carregarLista();
    } catch (err) {
      showAlert(`Não foi possível conectar à API em ${API_BASE_URL}.`);
    }
  }

  async function excluir(id) {
    if (!confirm("Tem certeza que deseja excluir este registro?")) return;
    try {
      const res = await fetch(`${apiUrl}/${id}`, { method: "DELETE", headers: authHeaders() });
      const payload = await res.json();
      if (!res.ok) {
        showAlert(payload.erro || "Não foi possível excluir.");
        return;
      }
      showAlert(`${config.singular} excluído com sucesso.`, "success");
      carregarLista();
    } catch (err) {
      showAlert(`Não foi possível conectar à API em ${API_BASE_URL}.`);
    }
  }

  tableBody.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const id = Number(btn.dataset.id);
    if (btn.dataset.action === "edit") {
      const item = state.items.find((i) => i.id === id);
      abrirModal(item);
    } else if (btn.dataset.action === "delete") {
      excluir(id);
    } else if (config.onAction) {
      // Ações extras definidas pela página (ex: "Rever", "Tentar novamente").
      config.onAction(btn.dataset.action, state.items.find((i) => i.id === id), btn);
    }
  });

  btnNovo?.addEventListener("click", () => abrirModal());
  btnCancelar?.addEventListener("click", fecharModal);
  modalBackdrop?.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) fecharModal();
  });
  form?.addEventListener("submit", salvar);

  carregarLista();

  // Interface pública para as páginas (ex: perguntas.html) reagirem a ações
  // extras, como "Gerar perguntas com IA", sem precisar de reload da página.
  return {
    recarregar: carregarLista,
    setFiltro,
    destacarTemporario,
  };
}
