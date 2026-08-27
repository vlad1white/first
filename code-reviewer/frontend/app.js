const codeInput = document.getElementById("code-input");
const languageSelect = document.getElementById("language-select");
const reviewBtn = document.getElementById("review-btn");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");
const issuesEl = document.getElementById("issues");

const SEVERITY_LABELS = {
  critical: "Критично",
  warning: "Предупреждение",
  suggestion: "Совет",
};

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.className = isError ? "status error" : "status";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

function renderIssue(issue) {
  const card = document.createElement("div");
  card.className = `issue-card ${issue.severity}`;

  const lineTag = issue.line && issue.line > 0 ? `<span class="line-tag">строка ${issue.line}</span>` : "";

  card.innerHTML = `
    <div class="issue-header">
      <span class="badge ${issue.severity}">${SEVERITY_LABELS[issue.severity] || issue.severity}</span>
      <span class="badge">${escapeHtml(issue.category)}</span>
      ${lineTag}
    </div>
    <div class="issue-title">${escapeHtml(issue.title)}</div>
    <p class="issue-description">${escapeHtml(issue.description)}</p>
    ${issue.suggestion ? `<div class="issue-suggestion">${escapeHtml(issue.suggestion)}</div>` : ""}
  `;
  return card;
}

function renderResult(data) {
  document.getElementById("score").textContent = `${data.overall_score}/10`;
  document.getElementById("summary-text").textContent = data.summary;

  issuesEl.innerHTML = "";
  if (!data.issues || data.issues.length === 0) {
    issuesEl.innerHTML = '<p class="no-issues">✅ Существенных проблем не найдено.</p>';
  } else {
    const order = { critical: 0, warning: 1, suggestion: 2 };
    const sorted = [...data.issues].sort((a, b) => (order[a.severity] ?? 3) - (order[b.severity] ?? 3));
    for (const issue of sorted) {
      issuesEl.appendChild(renderIssue(issue));
    }
  }

  result.classList.remove("hidden");
}

reviewBtn.addEventListener("click", async () => {
  const code = codeInput.value.trim();
  if (!code) {
    setStatus("Вставьте код для проверки", true);
    return;
  }

  reviewBtn.disabled = true;
  result.classList.add("hidden");
  setStatus("Claude анализирует код…");

  try {
    const res = await fetch("/api/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language: languageSelect.value || null }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Ошибка запроса");
    renderResult(data);
    setStatus("");
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    reviewBtn.disabled = false;
  }
});
