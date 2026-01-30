const el = (id) => document.getElementById(id);

function formatPrice(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return `$${n.toFixed(2)}`;
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResultCard(item, idx) {
  const name = escapeHtml(item?.name ?? "N/A");
  const desc = escapeHtml(item?.description ?? "");
  const category = escapeHtml((item?.category ?? "").toString().toUpperCase());
  const price = formatPrice(item?.price);
  const glb = item?.ar_model_glb;

  const modelSection = glb
    ? `
      <div class="mt-4">
        <div class="text-sm font-semibold text-slate-200">3D / AR</div>
        <div class="mt-2 overflow-hidden rounded-xl border border-slate-800">
          <model-viewer
            src="${escapeHtml(glb)}"
            ar
            ar-modes="scene-viewer webxr quick-look"
            camera-controls
            auto-rotate
            exposure="1"
            shadow-intensity="0.8"
            style="width: 100%; height: 420px;"
          ></model-viewer>
        </div>
        <div class="mt-2 text-xs text-slate-400">Tip: open on mobile, tap AR.</div>
      </div>
    `
    : `
      <div class="mt-4 rounded-xl border border-amber-800/60 bg-amber-900/10 px-4 py-3 text-sm text-amber-200">
        AR model not available.
      </div>
    `;

  return `
    <article class="rounded-2xl border border-slate-800 bg-slate-900/40 p-5">
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="text-sm text-slate-400">#${idx + 1}</div>
          <h2 class="mt-1 text-xl font-bold text-slate-100">${name}</h2>
          <div class="mt-2 text-sm text-slate-300">${desc}</div>
        </div>
        <div class="shrink-0 text-right">
          <div class="rounded-full border border-slate-700 bg-slate-950/30 px-3 py-1 text-xs font-semibold text-slate-200">${category || "N/A"}</div>
          <div class="mt-2 text-lg font-extrabold text-white">${price}</div>
        </div>
      </div>
      ${modelSection}
    </article>
  `;
}

async function runSearch() {
  const query = el("query").value.trim();
  const collection = el("collection").value;
  const topk = Number(el("topk").value || 5);

  el("status").textContent = "";
  el("results").innerHTML = "";

  if (!query) {
    el("status").textContent = "Type a query first.";
    return;
  }

  el("status").textContent = "Searching…";

  const params = new URLSearchParams({ q: query, collection, top_k: String(topk) });
  let res;
  try {
    res = await fetch(`/api/search?${params.toString()}`);
  } catch (e) {
    el("status").textContent = "Network error";
    el("results").innerHTML = `
      <div class="rounded-xl border border-rose-800/60 bg-rose-900/10 px-4 py-3 text-sm text-rose-200 md:col-span-2">
        Could not reach the API. Is the server running on this device?
      </div>
    `;
    return;
  }

  if (!res.ok) {
    const text = await res.text();
    el("status").textContent = `Error: ${res.status}`;
    el("results").innerHTML = `
      <div class="rounded-xl border border-rose-800/60 bg-rose-900/10 px-4 py-3 text-sm text-rose-200 md:col-span-2">
        ${escapeHtml(text || "Request failed")}
      </div>
    `;
    return;
  }

  const data = await res.json();
  const items = Array.isArray(data?.results) ? data.results : [];

  if (!items.length) {
    el("status").textContent = "No results.";
    el("results").innerHTML = `
      <div class="rounded-xl border border-slate-800 bg-slate-900/40 px-4 py-3 text-sm text-slate-200 md:col-span-2">
        No products found.
      </div>
    `;
    return;
  }

  el("status").textContent = `${items.length} result(s)`;
  el("results").innerHTML = items.map((it, idx) => renderResultCard(it, idx)).join("\n");
}

function clearAll() {
  el("query").value = "";
  el("results").innerHTML = "";
  el("status").textContent = "";
}

el("searchBtn").addEventListener("click", runSearch);
el("clearBtn").addEventListener("click", clearAll);
el("query").addEventListener("keydown", (e) => {
  if (e.key === "Enter") runSearch();
});
