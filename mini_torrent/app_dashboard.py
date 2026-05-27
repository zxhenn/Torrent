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
    @import url("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap");

    :root {
      --bg: #0f1215;
      --panel: #161a1e;
      --panel-2: #1c2126;
      --sidebar: #12161a;
      --line: #2a3238;
      --line-soft: #232a30;
      --text: #e7edf2;
      --muted: #9aa6af;
      --accent: #c7f30a;
      --accent-strong: #a3d906;
      --green: #8fe53d;
      --green-dark: #53b81f;
      --yellow: #f0d14a;
      --red: #ff6b6b;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: radial-gradient(1200px 520px at 10% -10%, #1f262c 0%, #11161a 45%, #0b0f12 100%);
      color: var(--text);
      font-family: "Space Grotesk", "Segoe UI", Arial, sans-serif;
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
      padding: 14px 12px;
    }

    .sidebar.open { left: 0; }

    .menu-toggle {
      display: none;
      min-width: 34px;
      height: 32px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
      color: var(--text);
      font-weight: 700;
      cursor: pointer;
    }

    .nav-scrim {
      position: fixed;
      inset: 0;
      background: rgba(7, 10, 12, 0.6);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
      z-index: 8;
    }

    .nav-scrim.visible {
      opacity: 1;
      pointer-events: auto;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 8px;
      height: 36px;
      color: #f1f5f8;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.3px;
    }

    .brand-mark {
      display: grid;
      place-items: center;
      width: 24px;
      height: 24px;
      border-radius: 8px;
      background: linear-gradient(135deg, var(--accent), #f4ff8a);
      color: #121417;
      font-weight: 800;
      box-shadow: 0 0 12px rgba(199, 243, 10, 0.35);
    }

    .nav { margin-top: 16px; }

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
      font-weight: 700;
      box-shadow: inset 2px 0 0 var(--accent);
    }

    .nav-count { color: var(--muted); }

    .hint {
      margin-top: 18px;
      padding: 12px;
      border: 1px solid var(--line);
      background: rgba(22, 26, 30, 0.9);
      color: var(--muted);
      line-height: 1.35;
      border-radius: 10px;
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
      min-height: 52px;
      padding: 10px 14px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.03);
    }

    .tool-button {
      min-width: 34px;
      height: 32px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
      color: var(--text);
      font-weight: 700;
      cursor: pointer;
    }

    .tool-button.text {
      padding: 0 10px;
      min-width: 72px;
    }

    .tool-button.primary {
      background: linear-gradient(135deg, var(--accent), #f1ff8d);
      color: #14181c;
      border-color: #d9ff5c;
      box-shadow: 0 6px 16px rgba(199, 243, 10, 0.25);
    }

    .tool-button.danger {
      color: var(--red);
    }

    .tool-button.warning {
      color: var(--yellow);
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

    .content {
      min-width: 0;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 345px;
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
      background: #1b2126;
      color: #b7c3cc;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    tr.selected { background: rgba(199, 243, 10, 0.12); }

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
      font-size: 11px;
      font-weight: 700;
      text-shadow: 0 1px 1px rgba(255, 255, 255, 0.2);
    }

    .side-panel {
      min-width: 0;
      overflow: auto;
      background: #151a1f;
      padding: 14px;
    }

    .panel-title {
      margin: 4px 0 10px;
      color: #e6edf2;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.3px;
      text-transform: uppercase;
    }

    .panel-tabs {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 12px;
    }

    .panel-tab {
      height: 34px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--panel-2);
      color: var(--muted);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .panel-tab.active {
      background: rgba(199, 243, 10, 0.15);
      color: var(--text);
      border-color: rgba(199, 243, 10, 0.45);
      box-shadow: inset 0 0 0 1px rgba(199, 243, 10, 0.25);
    }

    .panel-section { display: none; }
    .panel-section.active { display: block; }

    .form-section {
      margin-bottom: 13px;
      padding: 12px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 12px;
    }

    .form-section summary {
      cursor: pointer;
      color: #2f4050;
      font-weight: 800;
    }

    label {
      display: block;
      margin-top: 8px;
      color: #b7c3cc;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.2px;
    }

    input {
      width: 100%;
      margin-top: 4px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      font: inherit;
      background: #11161a;
      color: var(--text);
    }

    input::placeholder {
      color: #6f7a83;
    }

    .path-control {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 6px;
      align-items: end;
    }

    .path-control input { min-width: 0; }

    .path-button {
      min-width: 70px;
      height: 34px;
      margin-top: 4px;
      padding: 0 9px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #1a2026;
      color: var(--text);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .path-button:hover,
    .tool-button:hover {
      background: #202830;
      border-color: #3a4650;
    }

    .form-actions {
      display: flex;
      gap: 8px;
      margin-top: 10px;
    }

    .message {
      min-height: 18px;
      margin-top: 8px;
      color: #b7c3cc;
      font-size: 12px;
      line-height: 1.35;
    }

    .details {
      display: grid;
      grid-template-rows: auto 1fr;
      background: #14181c;
      border-top: 1px solid var(--line);
    }

    .tabs {
      display: flex;
      gap: 2px;
      height: 40px;
      padding: 0 12px;
      align-items: center;
      border-bottom: 1px solid var(--line);
      background: #14181c;
    }

    .tab {
      padding: 7px 11px;
      border-radius: 8px 8px 0 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .tab.active {
      background: var(--panel);
      border: 1px solid var(--line);
      border-bottom-color: var(--panel);
      color: var(--text);
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
      background: var(--panel);
      border-radius: 10px;
    }

    .piece {
      min-height: 13px;
      background: #222a31;
    }

    .piece.available { background: var(--green); }
    .piece.partial { background: var(--yellow); }

    .stats {
      display: grid;
      grid-template-columns: 115px 1fr;
      gap: 8px 12px;
      padding: 10px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 10px;
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

    .peer-list li.selected {
      background: rgba(199, 243, 10, 0.1);
      outline: 1px solid rgba(199, 243, 10, 0.35);
      padding: 6px;
      border-radius: 8px;
    }

    .job-meta {
      color: var(--muted);
      line-height: 1.35;
    }

    .job-message {
      margin-top: 4px;
      color: #35556e;
      line-height: 1.35;
    }

    .job-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 7px;
    }

    .job-actions button {
      height: 28px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
      color: var(--text);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    .job-actions button:disabled {
      color: #9aa6b2;
      cursor: default;
    }

    .job-actions button.danger { color: var(--red); }

    @media (max-width: 1000px) {
      .app { grid-template-columns: 1fr; }
      .sidebar {
        position: fixed;
        top: 0;
        left: -260px;
        width: 240px;
        height: 100vh;
        border-right: 1px solid var(--line);
        box-shadow: 10px 0 24px rgba(0, 0, 0, 0.35);
        z-index: 9;
        transition: left 0.2s ease;
      }
      .menu-toggle { display: inline-flex; align-items: center; justify-content: center; }
      .content { grid-template-columns: 1fr; }
      .side-panel { border-top: 1px solid var(--line); }
      .main { grid-template-rows: auto minmax(360px, 1fr) 340px; }
      .detail-grid { grid-template-columns: 1fr; }
      .toolbar { flex-wrap: wrap; justify-content: flex-start; }
      .status-pill { margin-left: 0; }
    }

    @media (max-width: 720px) {
      .toolbar { gap: 6px; }
      .tool-button.text { min-width: unset; padding: 0 8px; }
      .content { grid-template-columns: 1fr; }
      .table-wrap { border-right: none; }
      table { min-width: 640px; }
      .panel-tabs { grid-template-columns: 1fr; }
      .detail-grid { padding: 10px; }
    }

    @media (max-width: 520px) {
      body { font-size: 12px; }
      .toolbar { padding: 10px; }
      .tool-button { height: 30px; }
      .status-pill { width: 100%; text-align: center; }
      table { min-width: 560px; }
    }
  </style>
</head>
<body>
  <div class="nav-scrim" id="navScrim" onclick="toggleSidebar(false)"></div>
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
      <div class="hint firewall-hint">
        Across laptops: click Firewall once on the hub or seeder laptop if others time out.
      </div>
    </aside>

    <main class="main">
      <header class="toolbar">
        <button type="button" class="menu-toggle" aria-label="Open menu" onclick="toggleSidebar()">☰</button>
        <button type="button" class="tool-button primary" title="Refresh" onclick="loadStatus()">R</button>
        <button type="button" class="tool-button text" onclick="focusPanel('metaDetails')">Metadata</button>
        <button type="button" class="tool-button text" onclick="focusPanel('seedDetails')">Seed</button>
        <button type="button" class="tool-button text" onclick="focusPanel('leechDetails')">Leech</button>
        <button type="button" class="tool-button text" onclick="jobAction('resume')">Resume</button>
        <button type="button" class="tool-button text warning" onclick="jobAction('stop')">Stop</button>
        <button type="button" class="tool-button text danger" onclick="jobAction('delete')">Delete</button>
        <button type="button" class="tool-button text" onclick="setupFirewall()">Firewall</button>
        <button type="button" class="tool-button text" onclick="copyTrackerUrl()">Copy URL</button>
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

          <div class="panel-tabs" role="tablist" aria-label="Seed or leech">
            <button type="button" class="panel-tab" data-panel-tab="seed">Seeding</button>
            <button type="button" class="panel-tab" data-panel-tab="leech">Leeching</button>
          </div>

          <details class="form-section" id="metaDetails">
            <summary>Create Metadata</summary>
            <label>File to share</label>
            <div class="path-control">
              <input id="metaFile" value="sample_files/hello.txt">
              <button type="button" class="path-button" onclick="pickPath('metaFile', 'source_file')">Select</button>
            </div>
            <label>Chunk size in bytes</label>
            <input id="metaChunkSize" value="1048576">
            <label>Output .mtorrent path</label>
            <div class="path-control">
              <input id="metaOutput" value="torrents/hello.txt.mtorrent">
              <button type="button" class="path-button" onclick="pickPath('metaOutput', 'save_torrent')">Save As</button>
            </div>
            <div class="form-actions">
              <button type="button" class="tool-button text primary" onclick="createMetadata()">Create</button>
            </div>
            <div class="message" id="metaMessage"></div>
          </details>

          <div class="panel-section" data-panel-section="seed">
            <details class="form-section" id="seedDetails" open>
              <summary>Seed Complete File</summary>
              <label>Tracker URL</label>
              <input id="seedTracker">
              <label>.mtorrent path</label>
              <div class="path-control">
                <input id="seedTorrent" value="torrents/hello.txt.mtorrent">
                <button type="button" class="path-button" onclick="pickPath('seedTorrent', 'torrent_file', { inspect: true })">Select</button>
              </div>
              <label>Complete file path</label>
              <div class="path-control">
                <input id="seedFile" value="sample_files/hello.txt">
                <button type="button" class="path-button" onclick="pickPath('seedFile', 'source_file')">Select</button>
              </div>
              <label>This peer IP</label>
              <input id="seedHost">
              <label>Upload port</label>
              <input id="seedPort" value="9001">
              <label>Peer name</label>
              <input id="seedPeerId" value="seeder-1">
              <div class="form-actions">
                <button type="button" class="tool-button text primary" onclick="startSeed()">Start Seed</button>
              </div>
              <div class="message" id="seedMessage"></div>
            </details>
          </div>

          <div class="panel-section" data-panel-section="leech">
            <details class="form-section" id="leechDetails">
              <summary>Download File</summary>
              <label>Tracker URL</label>
              <input id="leechTracker">
              <label>.mtorrent path</label>
              <div class="path-control">
                <input id="leechTorrent" value="torrents/hello.txt.mtorrent">
                <button type="button" class="path-button" onclick="pickPath('leechTorrent', 'torrent_file', { inspect: true })">Select</button>
              </div>
              <label>Output file path</label>
              <div class="path-control">
                <input id="leechOutput" value="downloads/hello.txt">
                <button type="button" class="path-button" onclick="pickPath('leechOutput', 'download_output')">Save As</button>
              </div>
              <label>This peer IP</label>
              <input id="leechHost">
              <label>Upload port</label>
              <input id="leechPort" value="9002">
              <label>Peer name</label>
              <input id="leechPeerId" value="leecher-1">
              <div class="form-actions">
                <button type="button" class="tool-button text primary" onclick="startLeech()">Start Leech</button>
              </div>
              <div class="message" id="leechMessage"></div>
            </details>
          </div>

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
    let selectedPeerId = null;
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

    function pathBaseName(path) {
      return String(path || "").split(/[\\\\/]/).filter(Boolean).pop() || "";
    }

    function torrentOutputFor(path) {
      const filename = pathBaseName(path);
      return filename ? `torrents/${filename}.mtorrent` : "torrents/file.mtorrent";
    }

    function shouldReplacePath(value, defaults) {
      const text = String(value || "").trim();
      return !text || defaults.includes(text.replaceAll("\\\\", "/"));
    }

    function formMessageForField(fieldId) {
      if (fieldId.startsWith("meta")) return document.getElementById("metaMessage");
      if (fieldId.startsWith("seed")) return document.getElementById("seedMessage");
      return document.getElementById("leechMessage");
    }

    function autoFillMetadataOutput(sourcePath) {
      const output = document.getElementById("metaOutput");
      if (shouldReplacePath(output.value, ["torrents/hello.txt.mtorrent"])) {
        output.value = torrentOutputFor(sourcePath);
      }
    }

    async function inspectTorrent(fieldId) {
      const input = document.getElementById(fieldId);
      const target = formMessageForField(fieldId);
      if (!input.value.trim()) return null;

      const data = await requestJson("/api/inspect-torrent", {
        torrent_path: input.value,
      });

      if (fieldId === "leechTorrent") {
        const output = document.getElementById("leechOutput");
        if (shouldReplacePath(output.value, ["downloads/hello.txt", "downloads/downloaded-file"])) {
          output.value = data.default_output_path;
        }
      }

      target.textContent = `Loaded metadata for ${data.filename} (${data.total_chunks} chunks).`;
      return data;
    }

    async function pickPath(fieldId, purpose, options = {}) {
      const input = document.getElementById(fieldId);
      const target = formMessageForField(fieldId);
      const payload = {
        purpose,
        initial_path: input.value,
      };

      if (purpose === "save_torrent") {
        payload.suggested_name = `${pathBaseName(document.getElementById("metaFile").value) || "file"}.mtorrent`;
      }
      if (purpose === "download_output") {
        payload.suggested_name = pathBaseName(input.value) || "downloaded-file";
      }

      target.textContent = "Opening file picker...";
      try {
        const data = await requestJson("/api/pick-path", payload);
        if (!data.path) {
          target.textContent = "Selection cancelled.";
          return;
        }
        input.value = data.path;

        if (fieldId === "metaFile") {
          autoFillMetadataOutput(data.path);
        }
        if (options.inspect) {
          await inspectTorrent(fieldId);
        } else {
          target.textContent = `Selected ${data.path}.`;
        }
      } catch (error) {
        target.textContent = error.message;
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
        return `${escapeHtml(peer.peer_id)} (${peer.role}, ${peer.chunk_count}/${torrent.total_chunks || 0}) at ${escapeHtml(peer.host)}:${peer.port}, ${peer.updated_seconds_ago}s ago`;
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
        selectedPeerId = null;
        list.innerHTML = "<li>No local jobs yet.</li>";
        return;
      }
      if (!selectedPeerId || !jobs.some((job) => job.peer_id === selectedPeerId)) {
        selectedPeerId = jobs[0].peer_id;
      }
      list.innerHTML = jobs.map((job) => `
        <li class="${job.peer_id === selectedPeerId ? "selected" : ""}" data-select-peer="${escapeHtml(job.peer_id)}">
          <strong>${escapeHtml(job.peer_id)}</strong><br>
          <span class="job-meta">
            ${escapeHtml(job.role)} - ${escapeHtml(job.status)}<br>
            ${job.available_chunks}/${job.total_chunks} chunks (${pct(job.progress_percent)})<br>
            ${escapeHtml(job.host)}:${job.port}
          </span>
          <div class="job-message">${escapeHtml(job.message || "No message yet.")}</div>
          <div class="job-actions">
            <button type="button" data-job-action="resume" data-peer-id="${escapeHtml(job.peer_id)}" ${job.can_resume ? "" : "disabled"}>Resume</button>
            <button type="button" data-job-action="stop" data-peer-id="${escapeHtml(job.peer_id)}" ${job.can_stop ? "" : "disabled"}>Stop</button>
            <button type="button" class="danger" data-job-action="delete" data-peer-id="${escapeHtml(job.peer_id)}">Delete</button>
          </div>
        </li>
      `).join("");
      for (const item of list.querySelectorAll("[data-select-peer]")) {
        item.addEventListener("click", () => {
          selectedPeerId = item.dataset.selectPeer;
          renderJobs();
        });
      }
      for (const button of list.querySelectorAll("[data-job-action]")) {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          jobAction(button.dataset.jobAction, button.dataset.peerId);
        });
      }
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

    function currentJobId() {
      const jobs = latest.local_peers || [];
      if (selectedPeerId && jobs.some((job) => job.peer_id === selectedPeerId)) {
        return selectedPeerId;
      }
      if (jobs.length === 1) {
        selectedPeerId = jobs[0].peer_id;
        return selectedPeerId;
      }
      return "";
    }

    async function jobAction(action, peerId = "") {
      const selected = peerId || currentJobId();
      if (!selected) {
        document.getElementById("hubStatus").textContent = "Select a local job first.";
        return;
      }
      try {
        const data = await requestJson("/api/job-action", {
          action,
          peer_id: selected,
        });
        if (action === "delete") {
          selectedPeerId = null;
        } else {
          selectedPeerId = selected;
        }
        document.getElementById("hubStatus").textContent = `${data.action} ${data.peer_id}: ${data.status}`;
        await loadStatus();
      } catch (error) {
        document.getElementById("hubStatus").textContent = error.message;
      }
    }

    async function createMetadata() {
      const target = document.getElementById("metaMessage");
      try {
        const data = await requestJson("/api/create-torrent", {
          file_path: document.getElementById("metaFile").value,
          chunk_size: Number(document.getElementById("metaChunkSize").value),
          output_path: document.getElementById("metaOutput").value,
        });
        document.getElementById("seedTorrent").value = data.output_path;
        document.getElementById("leechTorrent").value = data.output_path;
        document.getElementById("seedFile").value = document.getElementById("metaFile").value;
        if (shouldReplacePath(document.getElementById("leechOutput").value, ["downloads/hello.txt", "downloads/downloaded-file"])) {
          document.getElementById("leechOutput").value = `downloads/${pathBaseName(document.getElementById("metaFile").value)}`;
        }
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

    async function setupFirewall() {
      const status = document.getElementById("hubStatus");
      status.textContent = "Waiting for Windows Firewall permission...";
      try {
        const data = await requestJson("/api/setup-firewall", {});
        status.textContent = data.message;
        alert(data.message);
      } catch (error) {
        status.textContent = error.message;
        alert(error.message);
      }
    }

    function setPanelTab(tab) {
      const tabs = document.querySelectorAll("[data-panel-tab]");
      const sections = document.querySelectorAll("[data-panel-section]");
      for (const item of tabs) {
        item.classList.toggle("active", item.dataset.panelTab === tab);
      }
      for (const section of sections) {
        const isActive = section.dataset.panelSection === tab;
        section.classList.toggle("active", isActive);
        const details = section.querySelector("details");
        if (details) details.open = isActive;
      }
      if (tab === "seed" || tab === "leech") {
        history.replaceState(null, "", `#${tab}`);
      }
    }

    function toggleSidebar(forceOpen) {
      const sidebar = document.querySelector(".sidebar");
      const scrim = document.getElementById("navScrim");
      const shouldOpen = forceOpen !== undefined ? forceOpen : !sidebar.classList.contains("open");
      sidebar.classList.toggle("open", shouldOpen);
      scrim.classList.toggle("visible", shouldOpen);
    }

    function focusPanel(id) {
      const panel = document.getElementById(id);
      if (id === "seedDetails") {
        setPanelTab("seed");
      } else if (id === "leechDetails") {
        setPanelTab("leech");
      }
      for (const item of document.querySelectorAll(".side-panel details.form-section")) {
        item.open = item.id === id;
      }
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

    const tabButtons = document.querySelectorAll("[data-panel-tab]");
    for (const button of tabButtons) {
      button.addEventListener("click", () => setPanelTab(button.dataset.panelTab));
    }
    setPanelTab(location.hash === "#leech" ? "leech" : "seed");

    loadStatus();
    setInterval(loadStatus, 2000);
  </script>
</body>
</html>
"""
