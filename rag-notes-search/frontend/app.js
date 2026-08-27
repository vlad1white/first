const API_BASE = "";

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const fileDropLabel = document.getElementById("file-drop-label");
const uploadStatus = document.getElementById("upload-status");
const uploadBtn = document.getElementById("upload-btn");
const docList = document.getElementById("doc-list");

const askForm = document.getElementById("ask-form");
const questionInput = document.getElementById("question-input");
const askBtn = document.getElementById("ask-btn");
const messages = document.getElementById("messages");

fileInput.addEventListener("change", () => {
  fileDropLabel.textContent = fileInput.files[0]?.name || "Загрузить .txt / .md / .pdf";
});

async function loadDocuments() {
  const res = await fetch(`${API_BASE}/api/documents`);
  const docs = await res.json();
  docList.innerHTML = "";
  if (docs.length === 0) {
    docList.innerHTML = '<li class="doc-item"><span class="meta">Пока пусто</span></li>';
    return;
  }
  for (const doc of docs) {
    const li = document.createElement("li");
    li.className = "doc-item";
    li.innerHTML = `
      <span class="meta">
        <span class="filename" title="${doc.filename}">${doc.filename}</span>
        <span class="chunks">${doc.num_chunks} фрагм.</span>
      </span>
      <button class="remove" title="Удалить" data-id="${doc.id}">✕</button>
    `;
    li.querySelector(".remove").addEventListener("click", () => deleteDocument(doc.id));
    docList.appendChild(li);
  }
}

async function deleteDocument(id) {
  await fetch(`${API_BASE}/api/documents/${id}`, { method: "DELETE" });
  loadDocuments();
}

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return;

  uploadBtn.disabled = true;
  uploadStatus.textContent = "Индексирую…";
  uploadStatus.className = "status";

  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/documents`, { method: "POST", body: formData });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Ошибка загрузки");
    }
    const doc = await res.json();
    uploadStatus.textContent = `Готово: ${doc.num_chunks} фрагментов проиндексировано`;
    fileInput.value = "";
    fileDropLabel.textContent = "Загрузить .txt / .md / .pdf";
    loadDocuments();
  } catch (err) {
    uploadStatus.textContent = err.message;
    uploadStatus.className = "status error";
  } finally {
    uploadBtn.disabled = false;
  }
});

function clearEmptyState() {
  const empty = messages.querySelector(".empty-state");
  if (empty) empty.remove();
}

function addUserBubble(text) {
  clearEmptyState();
  const row = document.createElement("div");
  row.className = "bubble-row user";
  row.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

function addAssistantBubble() {
  const row = document.createElement("div");
  row.className = "bubble-row assistant";
  row.innerHTML = `<div class="bubble spinner">Думаю…</div>`;
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return row;
}

function renderAssistantResult(row, answer, sources) {
  const bubble = row.querySelector(".bubble");
  bubble.className = "bubble";
  bubble.textContent = answer;

  if (sources.length > 0) {
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "sources";
    sourcesEl.innerHTML = sources
      .map(
        (s) => `
        <div class="source">
          <span class="score">${(s.score * 100).toFixed(0)}%</span>
          <strong>${escapeHtml(s.filename)}</strong><br />
          ${escapeHtml(s.text.slice(0, 220))}${s.text.length > 220 ? "…" : ""}
        </div>`
      )
      .join("");
    row.appendChild(sourcesEl);
  }
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

askForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  addUserBubble(question);
  questionInput.value = "";
  askBtn.disabled = true;
  const row = addAssistantBubble();

  try {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Ошибка запроса");
    renderAssistantResult(row, data.answer, data.sources);
  } catch (err) {
    renderAssistantResult(row, `⚠️ ${err.message}`, []);
  } finally {
    askBtn.disabled = false;
  }
});

loadDocuments();
