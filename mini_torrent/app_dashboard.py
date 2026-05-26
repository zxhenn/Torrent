"""Dashboard page for the ChunkShare desktop-style app."""

from __future__ import annotations


def render_app_html() -> str:
    """Return the ChunkShare app dashboard page."""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ChunkShare</title>
  <style>
    :root {
      --bg: #f3f6f8;
      --panel: #ffffff;
      --sidebar: #edf2f6;
      --line: #cfd8e1;
      --line-soft: #e5ebf0;
      --text: #1f2933;
      --muted: #647281;
      --blue: #5b9de6;
      --blue-dark: #2e74b8;
      --green: #92cd5a;
      --green-dark: #5ea132;
      --yellow: #e4bb4c;
      --red: #c44f4f;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 13px;
    }

    .app {
      display: grid;
      grid-template-columns: 230px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      background: var(--sidebar);
      border-right: 1px solid var(--line);
      padding: 12px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 8px;
      height: 36px;
      color: #20364d;
      font-size: 15px;
      font-weight: 700;
    }

    .brand-mark {
      display: grid;
      place-items: center;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--green);
      color: white;
      font-weight: 800;
    }

    .nav { margin-top: 16px; }

    .nav-item {
      display: flex;
      justify-content: space-between;
      padding: 9px 10px;
      border-radius: 4px;
      color: #33485e;
    }

    .nav-item.active {
      background: #d9eafa;
      color: #184f89;
      font-weight: 700;
    }

    .nav-count { color: var(--muted); }

    .hint {
      margin-top: 18px;
      padding: 10px;
      border: 1px solid var(--line);
      background: #f9fbfd;
      color: var(--muted);
      line-height: 1.35;
    }

    .main {
      min-width: 0;
      display: grid;
      grid-template-rows: auto minmax(250px, 1fr) 285px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 46px;
      padding: 8px 12px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }

    .tool-button {
      min-width: 34px;
      height: 30px;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: #f9fbfc;
      color: #34495e;
      font-weight: 700;
      cursor: pointer;
    }

    .tool-button.text {
      padding: 0 10px;
      min-width: 72px;
    }

    .tool-button.primary {
      background: #e9f3ff;
      color: #1d5e9e;
      border-color: #9fc5e8;
    }

    .tool-button.danger {
      color: var(--red);
    }

    .status-pill {
      margin-left: auto;
      padding: 6px 10px;
      border: 1px solid var(--line);
      border-radius: 4px;
      color: #405466;
      background: #f9fbfc;
      font-size: 12px;
    }

    .content {
      min-width: 0;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 335px;
      background: var(--panel);
    }

    .table-wrap { overflow: auto; border-right: 1px solid var(--line); }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 820px;
    }

    th, td {
      padding: 7px 9px;
      border-bottom: 1px solid var(--line-soft);
      text-align: left;
      white-space: nowrap;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 1;
      background: #edf3f8;
      color: #425566;
      font-size: 12px;
      font-weight: 700;
    }

    tr.selected { background: #e9f3ff; }

    .name {
      max-width: 260px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .hash {
      max-width: 150px;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--muted);
      font-family: Consolas, monospace;
      font-size: 12px;
    }

    .progress {
      position: relative;
      width: 150px;
      height: 22px;
      border: 1px solid #adc4d7;
      background: #edf2f7;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--blue-dark), var(--blue));
    }

    .progress.seeding .progress-fill {
      background: linear-gradient(90deg, var(--green-dark), var(--green));
    }

    .progress-label {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      color: #11283a;
      font-size: 12px;
      font-weight: 700;
    }

    .side-panel {
      min-width: 0;
      overflow: auto;
      background: #fbfcfd;
      padding: 12px;
    }

    .panel-title {
      margin: 4px 0 10px;
      color: #2f4050;
      font-size: 13px;
      font-weight: 800;
    }

    .form-section {
      margin-bottom: 13px;
      padding: 10px;
      border: 1px solid var(--line);
      background: white;
    }

    .form-section summary {
      cursor: pointer;
      color: #2f4050;
      font-weight: 800;
    }

    label {
      display: block;
      margin-top: 8px;
      color: #4d5e70;
      font-size: 12px;
      font-weight: 700;
    }

    input {
      width: 100%;
      margin-top: 4px;
      padding: 7px 8px;
      border: 1px solid var(--line);
      border-radius: 3px;
      font: inherit;
    }

    .form-actions {
      display: flex;
      gap: 8px;
      margin-top: 10px;
    }

    .message {
      min-height: 18px;
      margin-top: 8px;
      color: #35556e;
      font-size: 12px;
      line-height: 1.35;
    }

    .details {
      display: grid;
      grid-template-rows: auto 1fr;
      background: #fbfcfd;
      border-top: 1px solid var(--line);
    }

    .tabs {
      display: flex;
      gap: 2px;
      height: 36px;
      padding: 0 12px;
      align-items: center;
      border-bottom: 1px solid var(--line);
      background: #f2f5f8;
    }

    .tab {
      padding: 7px 11px;
      border-radius: 4px 4px 0 0;
      color: #435466;
      font-size: 12px;
      font-weight: 700;
    }

    .tab.active {
      background: white;
      border: 1px solid var(--line);
      border-bottom-color: white;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: 1fr 340px;
      gap: 15px;
      padding: 12px;
      overflow: auto;
    }

    .pieces {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(5px, 1fr));
      gap: 2px;
      min-height: 58px;
      padding: 8px;
      border: 1px solid var(--line);
      background: white;
    }

    .piece {
      min-height: 13px;
      background: #dfe7ee;
    }

    .piece.available { background: var(--green); }
    .piece.partial { background: var(--yellow); }

    .stats {
      display: grid;
      grid-template-columns: 115px 1fr;
      gap: 8px 12px;
      padding: 10px;
      border: 1px solid var(--line);
      background: white;
    }

    .stat-label {
      color: var(--muted);
      font-size: 12px;
    }

    .stat-value { font-weight: 700; }

    .empty {
      padding: 42px;
      color: var(--muted);
      text-align: center;
    }

    .peer-list {
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .peer-list li {
      padding: 6px 0;
      border-bottom: 1px solid var(--line-soft);
    }

    @media (max-width: 1000px) {
      .app { grid-template-columns: 1fr; }
      .sidebar { display: none; }
      .content { grid-template-columns: 1fr; }
      .side-panel { border-top: 1px solid var(--line); }
      .main { grid-template-rows: auto minmax(360px, 1fr) 340px; }
      .detail-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">C</span><span>ChunkShare</span></div>
      <nav class="nav">
        <div class="nav-item active"><span>Torrents</span><span class="nav-count" id="navTorrents">0</span></div>
        <div class="nav-item"><span>Seeders</span><span class="nav-count" id="navSeeders">0</span></div>
        <div class="nav-item"><span>Leechers</span><span class="nav-count" id="navLeechers">0</span></div>
        <div class="nav-item"><span>Peers</span><span class="nav-count" id="navPeers">0</span></div>
        <div class="nav-item"><span>Local Jobs</span><span class="nav-count" id="navJobs">0</span></div>
      </nav>
      <div class="hint">
        This dashboard opens first. Start seeding or leeching from the right panel.
      </div>
    </aside>

    <main class="main">
      <header class="toolbar">
        <button class="tool-button primary" title="Refresh" onclick="loadStatus()">R</button>
        <button class="tool-button text" onclick="focusPanel('seedDetails')">Seed</button>
        <button class="tool-button text" onclick="focusPanel('leechDetails')">Leech</button>
        <button class="tool-button text" onclick="focusPanel('metaDetails')">Metadata</button>
        <button class="tool-button text" onclick="copyTrackerUrl()">Copy URL</button>
        <span class="status-pill" id="hubStatus">Starting...</span>
      </header>

      <section class="content">
        <div class="table-wrap">
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
                <th>Hash</th>
              </tr>
            </thead>
            <tbody id="torrentRows">
              <tr><td colspan="10" class="empty">Dashboard ready. No torrents announced yet.</td></tr>
            </tbody>
          </table>
        </div>

        <aside class="side-panel">
          <div class="panel-title">Actions</div>

          <details class="form-section" id="metaDetails">
            <summary>Create Metadata</summary>
            <label>File to share</label>
            <input id="metaFile" value="sample_files/hello.txt">
            <label>Chunk size in bytes</label>
            <input id="metaChunkSize" value="262144">
            <label>Output .mtorrent path</label>
            <input id="metaOutput" value="torrents/hello.txt.mtorrent">
            <div class="form-actions">
              <button class="tool-button text primary" onclick="createMetadata()">Create</button>
            </div>
            <div class="message" id="metaMessage"></div>
          </details>

          <details class="form-section" id="seedDetails" open>
            <summary>Seed Complete File</summary>
            <label>Tracker URL</label>
            <input id="seedTracker">
            <label>.mtorrent path</label>
            <input id="seedTorrent" value="torrents/hello.txt.mtorrent">
            <label>Complete file path</label>
            <input id="seedFile" value="sample_files/hello.txt">
            <label>This peer IP</label>
            <input id="seedHost">
            <label>Upload port</label>
            <input id="seedPort" value="9001">
            <label>Peer name</label>
            <input id="seedPeerId" value="seeder-1">
            <div class="form-actions">
              <button class="tool-button text primary" onclick="startSeed()">Start Seed</button>
            </div>
            <div class="message" id="seedMessage"></div>
          </details>

          <details class="form-section" id="leechDetails">
            <summary>Download File</summary>
            <label>Tracker URL</label>
            <input id="leechTracker">
            <label>.mtorrent path</label>
            <input id="leechTorrent" value="torrents/hello.txt.mtorrent">
            <label>Output file path</label>
            <input id="leechOutput" value="downloads/hello.txt">
            <label>This peer IP</label>
            <input id="leechHost">
            <label>Upload port</label>
            <input id="leechPort" value="9002">
            <label>Peer name</label>
            <input id="leechPeerId" value="leecher-1">
            <div class="form-actions">
              <button class="tool-button text primary" onclick="startLeech()">Start Leech</button>
            </div>
            <div class="message" id="leechMessage"></div>
          </details>

          <div class="form-section">
            <div class="panel-title">Local Jobs</div>
            <ul class="peer-list" id="localJobs"></ul>
          </div>
        </aside>
      </section>

      <section class="details">
        <div class="tabs">
          <span class="tab active">Pieces</span>
          <span class="tab">Peers</span>
          <span class="tab">Hub</span>
        </div>
        <div class="detail-grid">
          <div>
            <div class="panel-title">Chunk Availability</div>
            <div class="pieces" id="pieces"></div>
          </div>
          <div>
            <div class="panel-title">Selected Torrent</div>
            <div class="stats" id="stats"></div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script>
    let selectedHash = null;
    let latest = { tracker: { torrents: [] }, local_peers: [] };

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function pct(value) {
      return `${Math.round((value || 0) * 10) / 10}%`;
    }

    function torrentStatus(torrent) {
      if (torrent.seeders > 0) return "Seeding";
      if (torrent.available_chunks > 0) return "Downloading";
      return "Waiting";
    }

    function setDefaults() {
      const trackerUrl = latest.tracker_url || "http://127.0.0.1:8000";
      const lanIp = latest.lan_ip || "127.0.0.1";
      for (const id of ["seedTracker", "leechTracker"]) {
        if (!document.getElementById(id).value) document.getElementById(id).value = trackerUrl;
      }
      for (const id of ["seedHost", "leechHost"]) {
        if (!document.getElementById(id).value) document.getElementById(id).value = lanIp;
      }
    }

    function renderRows() {
      const torrents = latest.tracker?.torrents || [];
      const body = document.getElementById("torrentRows");
      if (!torrents.length) {
        body.innerHTML = '<tr><td colspan="10" class="empty">Dashboard ready. No torrents announced yet.</td></tr>';
        renderDetails(null);
        return;
      }
      if (!selectedHash || !torrents.some((item) => item.file_hash === selectedHash)) {
        selectedHash = torrents[0].file_hash;
      }
      body.innerHTML = torrents.map((torrent, index) => {
        const status = torrentStatus(torrent);
        const rowClass = torrent.file_hash === selectedHash ? "selected" : "";
        const progressClass = status === "Seeding" ? "progress seeding" : "progress";
        return `
          <tr class="${rowClass}" onclick="selectTorrent('${torrent.file_hash}')">
            <td>${index + 1}</td>
            <td class="name">${escapeHtml(torrent.filename)}</td>
            <td>${escapeHtml(torrent.file_size_label)}</td>
            <td>
              <div class="${progressClass}">
                <div class="progress-fill" style="width:${torrent.availability_percent}%"></div>
                <div class="progress-label">${status} ${pct(torrent.availability_percent)}</div>
              </div>
            </td>
            <td>${pct(torrent.availability_percent)}</td>
            <td>${torrent.available_chunks}/${torrent.total_chunks || 0}</td>
            <td>${torrent.seeders}</td>
            <td>${torrent.leechers}</td>
            <td>${torrent.peer_count}</td>
            <td class="hash">${escapeHtml(torrent.file_hash)}</td>
          </tr>
        `;
      }).join("");
      renderDetails(torrents.find((item) => item.file_hash === selectedHash));
    }

    function renderDetails(torrent) {
      const pieces = document.getElementById("pieces");
      const stats = document.getElementById("stats");
      if (!torrent) {
        pieces.innerHTML = '<div class="empty">No torrent selected.</div>';
        stats.innerHTML = `
          <div class="stat-label">Hub</div><div class="stat-value">${escapeHtml(latest.tracker_url || "")}</div>
          <div class="stat-label">LAN IP</div><div class="stat-value">${escapeHtml(latest.lan_ip || "")}</div>
          <div class="stat-label">Status</div><div class="stat-value">Waiting for peers</div>
        `;
        return;
      }
      pieces.innerHTML = (torrent.pieces || []).map((state) => {
        const cls = state === 2 ? "piece available" : state === 1 ? "piece partial" : "piece";
        return `<span class="${cls}"></span>`;
      }).join("");
      const peerLines = (torrent.peers || []).map((peer) => {
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

    function renderSidebar() {
      const torrents = latest.tracker?.torrents || [];
      document.getElementById("navTorrents").textContent = torrents.length;
      document.getElementById("navSeeders").textContent = torrents.reduce((total, item) => total + item.seeders, 0);
      document.getElementById("navLeechers").textContent = torrents.reduce((total, item) => total + item.leechers, 0);
      document.getElementById("navPeers").textContent = torrents.reduce((total, item) => total + item.peer_count, 0);
      document.getElementById("navJobs").textContent = (latest.local_peers || []).length;
    }

    function renderJobs() {
      const jobs = latest.local_peers || [];
      const list = document.getElementById("localJobs");
      if (!jobs.length) {
        list.innerHTML = "<li>No local jobs yet.</li>";
        return;
      }
      list.innerHTML = jobs.map((job) => `
        <li>
          <strong>${escapeHtml(job.peer_id)}</strong><br>
          ${escapeHtml(job.role)} - ${escapeHtml(job.status)}<br>
          ${job.available_chunks}/${job.total_chunks} chunks on port ${job.port}
        </li>
      `).join("");
    }

    function selectTorrent(hash) {
      selectedHash = hash;
      renderRows();
    }

    async function requestJson(url, payload) {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Request failed");
      }
      return data;
    }

    async function createMetadata() {
      const target = document.getElementById("metaMessage");
      try {
        const data = await requestJson("/api/create-torrent", {
          file_path: document.getElementById("metaFile").value,
          chunk_size: Number(document.getElementById("metaChunkSize").value),
          output_path: document.getElementById("metaOutput").value,
        });
        target.textContent = `Created ${data.output_path} with ${data.total_chunks} chunks.`;
      } catch (error) {
        target.textContent = error.message;
      }
    }

    async function startSeed() {
      const target = document.getElementById("seedMessage");
      try {
        const data = await requestJson("/api/seed", {
          tracker_url: document.getElementById("seedTracker").value,
          torrent_path: document.getElementById("seedTorrent").value,
          file_path: document.getElementById("seedFile").value,
          host: document.getElementById("seedHost").value,
          port: Number(document.getElementById("seedPort").value),
          peer_id: document.getElementById("seedPeerId").value,
        });
        target.textContent = `Seeding as ${data.peer_id}.`;
        await loadStatus();
      } catch (error) {
        target.textContent = error.message;
      }
    }

    async function startLeech() {
      const target = document.getElementById("leechMessage");
      try {
        const data = await requestJson("/api/leech", {
          tracker_url: document.getElementById("leechTracker").value,
          torrent_path: document.getElementById("leechTorrent").value,
          output_path: document.getElementById("leechOutput").value,
          host: document.getElementById("leechHost").value,
          port: Number(document.getElementById("leechPort").value),
          peer_id: document.getElementById("leechPeerId").value,
        });
        target.textContent = `Leeching as ${data.peer_id}.`;
        await loadStatus();
      } catch (error) {
        target.textContent = error.message;
      }
    }

    async function copyTrackerUrl() {
      const text = latest.tracker_url || "";
      try {
        await navigator.clipboard.writeText(text);
        document.getElementById("hubStatus").textContent = `Copied ${text}`;
      } catch {
        document.getElementById("hubStatus").textContent = text;
      }
    }

    function focusPanel(id) {
      const panel = document.getElementById(id);
      panel.open = true;
      panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    async function loadStatus() {
      try {
        const response = await fetch("/api/status", { cache: "no-store" });
        latest = await response.json();
        setDefaults();
        renderSidebar();
        renderRows();
        renderJobs();
        document.getElementById("hubStatus").textContent = `Hub ${latest.tracker_url} - ${new Date().toLocaleTimeString()}`;
      } catch (error) {
        document.getElementById("hubStatus").textContent = "Dashboard cannot reach app server";
      }
    }

    loadStatus();
    setInterval(loadStatus, 2000);
  </script>
</body>
</html>
"""
