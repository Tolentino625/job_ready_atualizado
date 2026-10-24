(function () {
  const LINKS = [
    { href: "index.html", label: "Início", key: "home" },
    { href: "curriculos.html", label: "Currículos", key: "curriculos" },
    { href: "perguntas.html", label: "Perguntas", key: "perguntas" },
    { href: "entrevistas.html", label: "Entrevistas", key: "entrevistas" },
    { href: "respostas.html", label: "Respostas", key: "respostas" },
    { href: "feedbacks.html", label: "Feedbacks", key: "feedbacks" },
    { href: "lembretes.html", label: "Lembretes de estudo", key: "lembretes" },
  ];

  function iniciais(nome) {
    const partes = String(nome ?? "").trim().split(/\s+/).filter(Boolean);
    if (!partes.length) return "?";
    const primeira = partes[0][0] ?? "";
    const ultima = partes.length > 1 ? partes[partes.length - 1][0] ?? "" : "";
    return (primeira + ultima).toUpperCase();
  }

  function renderSidebar() {
    const container = document.getElementById("sidebar");
    if (!container) return;
    const active = container.dataset.active || "home";
    const user = typeof getAuthUser === "function" ? getAuthUser() : null;

    const links = LINKS.map(
      (link) =>
        `<a href="${link.href}" class="${link.key === active ? "active" : ""}">${link.label}</a>`
    ).join("\n");

    container.innerHTML = `
      <div class="brand">JobReady</div>
      <div class="tagline">Preparação para entrevistas</div>
      <nav>${links}</nav>
      <div class="sidebar-account">
        <a href="usuarios.html" class="sidebar-profile${active === "perfil" ? " active" : ""}" title="Ver meu perfil">
          <span class="sidebar-avatar">${escapeHtml(iniciais(user?.nome))}</span>
          <span class="sidebar-profile-info">
            <strong>${user ? escapeHtml(user.nome) : "Perfil"}</strong>
            <small>Ver perfil</small>
          </span>
        </a>
        <button type="button" class="logout-link" id="btn-logout">Sair</button>
      </div>
    `;

    document.getElementById("btn-logout")?.addEventListener("click", logout);
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  document.addEventListener("DOMContentLoaded", renderSidebar);
})();
