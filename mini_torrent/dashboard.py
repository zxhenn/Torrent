"""HTML dashboard for the tracker."""

from __future__ import annotations


def format_bytes(size: int | None) -> str:
    """Convert a byte count into a short human-readable label."""
    if size is None:
        return "Unknown"
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.1f} {units[unit_index]}"


def render_dashboard_html() -> str:
    """Return the tracker dashboard page."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ChunkShare Dashboard</title>
  <style>
    @import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap");

    :root {
      --line: #2a3238;
      --line-soft: #232a30;
      --bg: #0f1215;
      --panel: #161a1e;
      --panel-2: #1c2126;
      --text: #e7edf2;
      --muted: #9aa6af;
      --accent: #c7f30a;
      --accent-strong: #a3d906;
      --green: #8fe53d;
      --green-dark: #53b81f;
      --yellow: #f0d14a;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: radial-gradient(1200px 520px at 10% -10%, #1f262c 0%, #11161a 45%, #0b0f12 100%);
      color: var(--text);
      font-family: "Space Grotesk", "Segoe UI", Arial, sans-serif;
      font-size: 14px;
    }

    .shell {
      display: grid;
      grid-template-columns: 230px 1fr;
      min-height: 100vh;
    }

    .sidebar {
      background: #12161a;
      border-right: 1px solid var(--line);
      padding: 14px 12px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 8px;
      height: 36px;
      font-weight: 700;
      color: #f1f5f8;
      letter-spacing: 0.3px;
    }

    .brand-mark {
      display: grid;
      place-items: center;
      width: 22px;
      height: 22px;
      border-radius: 8px;
      background: linear-gradient(135deg, var(--accent), #f4ff8a);
      color: #121417;
      font-size: 13px;
      box-shadow: 0 0 12px rgba(199, 243, 10, 0.35);
    }

    .nav {
      margin-top: 14px;
    }

    .nav-item {
      display: flex;
      justify-content: space-between;
      padding: 9px 10px;
      border-radius: 8px;
      color: #c7d2dc;
    }

    .nav-item.active {
      background: rgba(199, 243, 10, 0.12);
      color: #f1f5f8;
      font-weight: 600;
      box-shadow: inset 2px 0 0 var(--accent);
    }

    .nav-count {
      color: var(--muted);
    }

    .main {
      min-width: 0;
      display: grid;
      grid-template-rows: auto minmax(240px, 1fr) 260px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      height: 52px;
      padding: 0 14px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }

    .tool-button {
      display: grid;
      place-items: center;
      width: 30px;
      height: 30px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
      color: var(--text);
      font-weight: 700;
    }

    .status-pill {
      margin-left: auto;
      padding: 6px 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      background: var(--panel-2);
      font-size: 12px;
    }

    .table-wrap {
      overflow: auto;
      background: var(--panel);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 860px;
    }

    th, td {
      padding: 8px 10px;
      border-bottom: 1px solid var(--line-soft);
      text-align: left;
      white-space: nowrap;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 1;
      background: #1b2126;
      color: #b7c3cc;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    tr.selected {
      background: rgba(199, 243, 10, 0.12);
    }

    .name {
      max-width: 280px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .hash {
      max-width: 180px;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--muted);
      font-family: Consolas, monospace;
      font-size: 12px;
    }

    .progress {
      position: relative;
      height: 22px;
      width: 160px;
      border: 1px solid #313b43;
      background: #14181c;
      overflow: hidden;
      border-radius: 999px;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-strong), var(--accent));
    }

    .progress.seeding .progress-fill {
      background: linear-gradient(90deg, var(--green-dark), var(--green));
    }

    .progress-label {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      color: #101317;
      font-size: 12px;
      font-weight: 600;
      text-shadow: 0 1px 1px rgba(255, 255, 255, 0.2);
    }

    .details {
      display: grid;
      grid-template-rows: auto 1fr;
      background: #14181c;
      border-top: 1px solid var(--line);
    }

    .tabs {
      display: flex;
      align-items: center;
      gap: 2px;
      height: 40px;
      padding: 0 12px;
      border-bottom: 1px solid var(--line);
      background: #14181c;
    }

    .tab {
      padding: 7px 11px;
      border-radius: 8px 8px 0 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }

    .tab.active {
      background: var(--panel);
      border: 1px solid var(--line);
      border-bottom-color: var(--panel);
      color: var(--text);
    }

    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 330px;
      gap: 16px;
      padding: 14px;
      overflow: auto;
    }

    .section-title {
      margin-bottom: 8px;
      color: #2d3f50;
      font-size: 13px;
      font-weight: 700;
    }

    .pieces {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(5px, 1fr));
      gap: 2px;
      min-height: 60px;
      padding: 8px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 10px;
    }

    .piece {
      min-height: 14px;
      background: #222a31;
    }

    .piece.available {
      background: var(--green);
    }

    .piece.partial {
      background: var(--yellow);
    }

    .stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 18px;
      align-content: start;
      padding: 10px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 10px;
    }

    .stat-label {
      color: var(--muted);
      font-size: 12px;
    }

    .stat-value {
      font-weight: 700;
    }

    .empty {
      padding: 42px;
      color: var(--muted);
      text-align: center;
    }

    @media (max-width: 850px) {
      .shell {
        grid-template-columns: 1fr;
      }

      .sidebar {
        display: none;
      }

      .main {
        grid-template-rows: auto minmax(260px, 1fr) 300px;
      }

      .detail-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 720px) {
      .toolbar { flex-wrap: wrap; gap: 6px; height: auto; padding: 10px; }
      .status-pill { margin-left: 0; }
      table { min-width: 640px; }
      .detail-grid { padding: 10px; }
    }

    @media (max-width: 520px) {
      body { font-size: 12px; }
      .status-pill { width: 100%; text-align: center; }
      table { min-width: 560px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">M</span>
        <span>ChunkShare</span>
      </div>
      <nav class="nav">
        <div class="nav-item active"><span>Torrents</span><span class="nav-count" id="navTorrents">0</span></div>
        <div class="nav-item"><span>Seeding</span><span class="nav-count" id="navSeeding">0</span></div>
        <div class="nav-item"><span>Leeching</span><span class="nav-count" id="navLeeching">0</span></div>
        <div class="nav-item"><span>Peers</span><span class="nav-count" id="navPeers">0</span></div>
        <div class="nav-item"><span>Tracker</span><span class="nav-count">online</span></div>
      </nav>
    </aside>

    <main class="main">
      <header class="toolbar">
        <button class="tool-button" title="Add torrent">+</button>
        <button class="tool-button" title="Start">&gt;</button>
        <button class="tool-button" title="Stop">[]</button>
        <button class="tool-button" title="Refresh" onclick="loadState()">R</button>
        <span class="status-pill" id="lastUpdated">Waiting for tracker data</span>
      </header>

      <section class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Size</th>
              <th>Status</th>
              <th>Availability</th>
              <th>Chunks</th>
              <th>Seeders</th>
              <th>Leechers</th>
              <th>Peers</th>
              <th>File Hash</th>
            </tr>
          </thead>
          <tbody id="torrentRows">
            <tr><td colspan="10" class="empty">No peers have announced yet.</td></tr>
          </tbody>
        </table>
      </section>

      <section class="details">
        <div class="tabs">
          <span class="tab active">Pieces</span>
          <span class="tab">Peers</span>
          <span class="tab">Tracker</span>
        </div>
        <div class="detail-grid">
          <div>
            <div class="section-title">Chunk Availability</div>
            <div class="pieces" id="pieces"></div>
          </div>
          <div>
            <div class="section-title">Selected Torrent</div>
            <div class="stats" id="stats"></div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script>
    let selectedHash = null;
    let latestState = { torrents: [] };

    function percent(value) {
      return `${Math.round(value * 10) / 10}%`;
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function torrentStatus(torrent) {
      if (torrent.seeders > 0) {
        return "Seeding";
      }
      if (torrent.available_chunks > 0) {
        return "Downloading";
      }
      return "Waiting";
    }

    function renderRows() {
      const body = document.getElementById("torrentRows");
      const torrents = latestState.torrents || [];
      if (!torrents.length) {
        body.innerHTML = '<tr><td colspan="10" class="empty">No peers have announced yet. Start a seeder or leecher.</td></tr>';
        renderDetails(null);
        return;
      }

      if (!selectedHash || !torrents.some((torrent) => torrent.file_hash === selectedHash)) {
        selectedHash = torrents[0].file_hash;
      }

      body.innerHTML = torrents.map((torrent, index) => {
        const selected = torrent.file_hash === selectedHash ? "selected" : "";
        const status = torrentStatus(torrent);
        const progressClass = status === "Seeding" ? "progress seeding" : "progress";
        return `
          <tr class="${selected}" onclick="selectTorrent('${torrent.file_hash}')">
            <td>${index + 1}</td>
            <td class="name">${escapeHtml(torrent.filename)}</td>
            <td>${escapeHtml(torrent.file_size_label)}</td>
            <td>
              <div class="${progressClass}">
                <div class="progress-fill" style="width: ${torrent.availability_percent}%"></div>
                <div class="progress-label">${status} ${percent(torrent.availability_percent)}</div>
              </div>
            </td>
            <td>${percent(torrent.availability_percent)}</td>
            <td>${torrent.available_chunks}/${torrent.total_chunks || 0}</td>
            <td>${torrent.seeders}</td>
            <td>${torrent.leechers}</td>
            <td>${torrent.peer_count}</td>
            <td class="hash">${escapeHtml(torrent.file_hash)}</td>
          </tr>
        `;
      }).join("");

      renderDetails(torrents.find((torrent) => torrent.file_hash === selectedHash));
    }

    function renderDetails(torrent) {
      const pieces = document.getElementById("pieces");
      const stats = document.getElementById("stats");
      if (!torrent) {
        pieces.innerHTML = '<div class="empty">No torrent selected.</div>';
        stats.innerHTML = "";
        return;
      }

      const pieceStates = torrent.pieces || [];
      pieces.innerHTML = pieceStates.map((state) => {
        const className = state === 2 ? "piece available" : state === 1 ? "piece partial" : "piece";
        return `<span class="${className}"></span>`;
      }).join("");

      const peerLines = torrent.peers.map((peer) => {
        return `${escapeHtml(peer.peer_id)} (${peer.role}, ${peer.chunk_count}/${torrent.total_chunks || 0})`;
      }).join("<br>");

      stats.innerHTML = `
        <div class="stat-label">Name</div><div class="stat-value">${escapeHtml(torrent.filename)}</div>
        <div class="stat-label">Status</div><div class="stat-value">${torrentStatus(torrent)}</div>
        <div class="stat-label">Size</div><div class="stat-value">${escapeHtml(torrent.file_size_label)}</div>
        <div class="stat-label">Chunks</div><div class="stat-value">${torrent.available_chunks}/${torrent.total_chunks || 0}</div>
        <div class="stat-label">Seeders</div><div class="stat-value">${torrent.seeders}</div>
        <div class="stat-label">Leechers</div><div class="stat-value">${torrent.leechers}</div>
        <div class="stat-label">Peers</div><div class="stat-value">${torrent.peer_count}</div>
        <div class="stat-label">Peer List</div><div>${peerLines || "No peers"}</div>
      `;
    }

    function selectTorrent(fileHash) {
      selectedHash = fileHash;
      renderRows();
    }

    function updateSidebar() {
      const torrents = latestState.torrents || [];
      document.getElementById("navTorrents").textContent = torrents.length;
      document.getElementById("navSeeding").textContent = torrents.reduce((total, item) => total + item.seeders, 0);
      document.getElementById("navLeeching").textContent = torrents.reduce((total, item) => total + item.leechers, 0);
      document.getElementById("navPeers").textContent = torrents.reduce((total, item) => total + item.peer_count, 0);
    }

    async function loadState() {
      try {
        const response = await fetch("/api/state", { cache: "no-store" });
        latestState = await response.json();
        updateSidebar();
        renderRows();
        document.getElementById("lastUpdated").textContent = `Updated ${new Date().toLocaleTimeString()}`;
      } catch (error) {
        document.getElementById("lastUpdated").textContent = "Tracker dashboard cannot load state";
      }
    }

    loadState();
    setInterval(loadState, 2500);
  </script>
</body>
</html>
"""
