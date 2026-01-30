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
      <div class="mt-5">
        <div class="text-sm font-semibold text-slate-200">3D / AR Preview</div>
        <div class="mt-3 overflow-hidden rounded-2xl border border-white/5">
          <model-viewer
            src="${escapeHtml(glb)}"
            ar
            ar-modes="scene-viewer webxr quick-look"
            camera-controls
            auto-rotate
            exposure="1.2"
            shadow-intensity="1"
            style="width: 100%; height: 380px;"
          ></model-viewer>
        </div>
        <div class="mt-3 text-xs text-slate-400">💡 Open on mobile and tap AR button to view in your space</div>
      </div>
    `
    : `
      <div class="mt-4 rounded-xl border border-amber-700/50 bg-amber-900/20 px-4 py-3 text-sm text-amber-300">
        ⚠️ AR model not available for this product
      </div>
    `;

  return `
    <article class="group overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/80 to-slate-800/80 p-6 shadow-lg backdrop-blur transition hover:border-purple-500/30 hover:shadow-2xl hover:shadow-purple-500/20">
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1">
          <div class="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-300">
            #${idx + 1}
          </div>
          <h2 class="mt-3 text-2xl font-extrabold text-white">${name}</h2>
          <p class="mt-2 text-sm leading-relaxed text-slate-300">${desc}</p>
        </div>
        <div class="shrink-0 text-right">
          <div class="rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-slate-200">${category || "N/A"}</div>
          <div class="mt-3 text-3xl font-extrabold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">${price}</div>
        </div>
      </div>
      ${modelSection}
      <button class="mt-5 w-full rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 px-6 py-3 font-semibold text-white shadow-lg shadow-purple-500/20 transition hover:scale-105 hover:shadow-purple-500/40">
        Add to Cart
      </button>
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
