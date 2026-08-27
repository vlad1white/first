const form = document.getElementById("ticker-form");
const symbolInput = document.getElementById("symbol-input");
const questionInput = document.getElementById("question-input");
const submitBtn = document.getElementById("submit-btn");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.className = isError ? "status error" : "status";
}

function sentimentClass(label) {
  const l = (label || "").toLowerCase();
  if (l.includes("bullish")) return "bullish";
  if (l.includes("bearish")) return "bearish";
  return "neutral";
}

function renderSparkline(history) {
  const svg = document.getElementById("sparkline");
  svg.innerHTML = "";
  if (!history || history.length < 2) return;

  const closes = history.map((p) => p.close);
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;
  const w = 300;
  const h = 60;
  const step = w / (closes.length - 1);

  const points = closes
    .map((c, i) => {
      const x = i * step;
      const y = h - ((c - min) / range) * (h - 8) - 4;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const rising = closes[closes.length - 1] >= closes[0];
  const color = rising ? "#4ade80" : "#ff6b6b";

  const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
  polyline.setAttribute("points", points);
  polyline.setAttribute("fill", "none");
  polyline.setAttribute("stroke", color);
  polyline.setAttribute("stroke-width", "2");
  svg.appendChild(polyline);
}

function renderQuote(quote) {
  document.getElementById("q-symbol").textContent = quote.symbol;
  document.getElementById("q-price").textContent = `$${quote.price.toFixed(2)}`;

  const changeEl = document.getElementById("q-change");
  const sign = quote.change >= 0 ? "+" : "";
  changeEl.textContent = `${sign}${quote.change.toFixed(2)} (${sign}${quote.change_percent}%)`;
  changeEl.className = `q-change ${quote.change >= 0 ? "positive" : "negative"}`;

  document.getElementById("q-prev").textContent = `$${quote.previous_close.toFixed(2)}`;
  document.getElementById("q-volume").textContent = quote.volume.toLocaleString("ru-RU");
  document.getElementById("q-date").textContent = quote.latest_trading_day;
}

function renderNews(news) {
  const list = document.getElementById("news-list");
  list.innerHTML = "";
  if (!news || news.length === 0) {
    list.innerHTML = "<li>Свежих новостей не найдено.</li>";
    return;
  }
  for (const item of news) {
    const li = document.createElement("li");
    li.innerHTML = `
      <a href="${item.url}" target="_blank" rel="noopener">${escapeHtml(item.title)}</a>
      <div class="news-meta">
        <span class="sentiment-badge ${sentimentClass(item.sentiment_label)}">${item.sentiment_label || "n/a"}</span>
        <span>${escapeHtml(item.source)}</span>
      </div>
    `;
    list.appendChild(li);
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const symbol = symbolInput.value.trim();
  if (!symbol) return;
  const question = questionInput.value.trim();

  submitBtn.disabled = true;
  result.classList.add("hidden");
  setStatus("Загружаю данные и спрашиваю Claude…");

  try {
    const res = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, question: question || null }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Ошибка запроса");

    renderQuote(data.quote);
    renderSparkline(data.history);
    document.getElementById("explanation-text").textContent = data.explanation;
    renderNews(data.news);

    result.classList.remove("hidden");
    setStatus("");
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    submitBtn.disabled = false;
  }
});
