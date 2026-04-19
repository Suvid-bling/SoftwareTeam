// ---------------------------------------------------------------------------
// SdeTeam Web UI — Frontend Logic
// ---------------------------------------------------------------------------

const API = "";
let ws = null;
let termWs = null;
let isRunning = false;
const selectedRoles = new Set();

// DOM refs
const roleList = document.getElementById("role-list");
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const ideaInput = document.getElementById("idea-input");
const btnRun = document.getElementById("btn-run");
const btnStop = document.getElementById("btn-stop");
const statusBadge = document.getElementById("status-badge");
const fileTree = document.getElementById("file-tree");
const filePreview = document.getElementById("file-preview");
const previewFilename = document.getElementById("preview-filename");
const previewContent = document.getElementById("preview-content");
const btnClosePreview = document.getElementById("btn-close-preview");
const btnRefreshFiles = document.getElementById("btn-refresh-files");
const investmentInput = document.getElementById("investment");

// Tab refs
const tabChat = document.getElementById("tab-chat");
const tabTerminal = document.getElementById("tab-terminal");
const tabAgents = document.getElementById("tab-agents");
const panelChat = document.getElementById("panel-chat");
const panelTerminal = document.getElementById("panel-terminal");
const panelAgents = document.getElementById("panel-agents");
const terminalOutput = document.getElementById("terminal-output");
const terminalInput = document.getElementById("terminal-input");
const btnSendCmd = document.getElementById("btn-send-cmd");

// Agent process refs
const agentSlider = document.getElementById("agent-slider");
const agentLogsGrid = document.getElementById("agent-logs-grid");
const agentEmpty = document.getElementById("agent-empty");
const sliderLeft = document.getElementById("slider-left");
const sliderRight = document.getElementById("slider-right");

// Context menu refs
const contextMenu = document.getElementById("context-menu");
const ctxRun = document.getElementById("ctx-run");
const ctxStop = document.getElementById("ctx-stop");
let contextMenuTarget = null;
const runningProjects = new Set();

// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------

const ALL_TABS = ["chat", "terminal", "agents"];
const TAB_BTNS = { chat: tabChat, terminal: tabTerminal, agents: tabAgents };
const PANELS = { chat: panelChat, terminal: panelTerminal, agents: panelAgents };

function switchTab(tab) {
  ALL_TABS.forEach((t) => {
    const btn = TAB_BTNS[t];
    const panel = PANELS[t];
    const isActive = t === tab;
    btn.classList.toggle("border-blue-500", isActive);
    btn.classList.toggle("text-blue-400", isActive);
    btn.classList.toggle("border-transparent", !isActive);
    btn.classList.toggle("text-gray-500", !isActive);
    panel.classList.toggle("hidden", !isActive);
  });
  if (tab === "terminal" && !termWs) connectTerminal();
  if (tab === "agents") refreshAgentPanel();
}

tabChat.addEventListener("click", () => switchTab("chat"));
tabTerminal.addEventListener("click", () => switchTab("terminal"));
tabAgents.addEventListener("click", () => switchTab("agents"));

// ---------------------------------------------------------------------------
// Terminal WebSocket
// ---------------------------------------------------------------------------

function connectTerminal() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  termWs = new WebSocket(`${proto}//${location.host}/ws/terminal`);
  termWs.onopen = () => { terminalOutput.textContent = ""; appendTerminal("Connected to workspace shell.\n"); };
  termWs.onmessage = (e) => appendTerminal(e.data);
  termWs.onclose = () => { appendTerminal("\n[disconnected]\n"); termWs = null; };
}

function appendTerminal(text) {
  terminalOutput.textContent += text;
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function sendTerminalCommand() {
  const cmd = terminalInput.value;
  if (!cmd || !termWs) return;
  if (termWs.readyState === WebSocket.OPEN) { termWs.send(cmd + "\n"); terminalInput.value = ""; }
}

btnSendCmd.addEventListener("click", sendTerminalCommand);
terminalInput.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); sendTerminalCommand(); } });

// ---------------------------------------------------------------------------
// Roles
// ---------------------------------------------------------------------------

async function loadRoles() {
  const res = await fetch(`${API}/api/roles`);
  const roles = await res.json();
  roleList.innerHTML = "";
  const defaults = ["ProductManager", "Architect", "ProjectManager", "Engineer", "QaEngineer"];
  roles.forEach((r) => {
    if (defaults.includes(r.name)) selectedRoles.add(r.name);
    const el = document.createElement("label");
    el.className = "flex items-start gap-2 p-2 rounded-lg hover:bg-gray-800 cursor-pointer select-none";
    el.innerHTML = `
      <input type="checkbox" class="mt-0.5 accent-blue-500" value="${r.name}"
             ${selectedRoles.has(r.name) ? "checked" : ""} />
      <span>
        <span class="block text-sm font-medium">${r.name}</span>
        <span class="block text-xs text-gray-500">${r.desc}</span>
      </span>`;
    el.querySelector("input").addEventListener("change", (e) => {
      e.target.checked ? selectedRoles.add(r.name) : selectedRoles.delete(r.name);
    });
    roleList.appendChild(el);
  });
}

// ---------------------------------------------------------------------------
// Chat / Run
// ---------------------------------------------------------------------------

function appendChat(text, type = "log") {
  const div = document.createElement("div");
  if (type === "user") div.className = "bg-blue-900/40 border border-blue-800 rounded-lg px-3 py-2 text-blue-200 whitespace-pre-wrap";
  else if (type === "error") div.className = "text-red-400 whitespace-pre-wrap";
  else if (type === "system") div.className = "text-green-400 whitespace-pre-wrap";
  else div.className = "text-gray-400 whitespace-pre-wrap";
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function setRunning(running) {
  isRunning = running;
  btnRun.classList.toggle("hidden", running);
  btnStop.classList.toggle("hidden", !running);
  statusBadge.textContent = running ? "Running…" : "Idle";
  statusBadge.className = running
    ? "text-xs px-2 py-0.5 rounded-full bg-green-800 text-green-300 animate-pulse"
    : "text-xs px-2 py-0.5 rounded-full bg-gray-700";
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const idea = ideaInput.value.trim();
  if (!idea) return;
  if (selectedRoles.size === 0) { appendChat("Please select at least one role.", "error"); return; }
  appendChat(idea, "user");
  ideaInput.value = "";
  const body = { idea, roles: [...selectedRoles], investment: parseFloat(investmentInput.value) || 10, n_round: 100 };
  try {
    const res = await fetch(`${API}/api/run`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await res.json();
    if (data.error) { appendChat(data.error, "error"); return; }
    setRunning(true);
    connectWS();
    startAgentPolling();
  } catch (err) { appendChat(`Failed to start: ${err.message}`, "error"); }
});

btnStop.addEventListener("click", async () => {
  try { await fetch(`${API}/api/stop`, { method: "POST" }); appendChat("Stop requested.", "system"); }
  catch (err) { appendChat(`Stop failed: ${err.message}`, "error"); }
});

// ---------------------------------------------------------------------------
// WebSocket log streaming
// ---------------------------------------------------------------------------

function connectWS() {
  if (ws) ws.close();
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${proto}//${location.host}/ws/logs`);
  ws.onmessage = (e) => {
    const line = e.data;
    if (line.startsWith("[error]")) appendChat(line, "error");
    else if (line.startsWith("[system]")) {
      appendChat(line, "system");
      if (line.includes("finished") || line.includes("cancelled")) { setRunning(false); refreshFiles(); }
    } else appendChat(line, "log");
  };
  ws.onclose = () => setTimeout(pollStatus, 2000);
}

async function pollStatus() {
  try {
    const res = await fetch(`${API}/api/status`);
    const data = await res.json();
    if (!data.running && isRunning) { setRunning(false); refreshFiles(); }
  } catch (_) {}
}

// ---------------------------------------------------------------------------
// Agent Process panel
// ---------------------------------------------------------------------------

const ROLE_COLORS = {
  ProductManager: "border-purple-600 bg-purple-900/20",
  Architect: "border-cyan-600 bg-cyan-900/20",
  ProjectManager: "border-yellow-600 bg-yellow-900/20",
  Engineer: "border-green-600 bg-green-900/20",
  QaEngineer: "border-red-600 bg-red-900/20",
  Searcher: "border-orange-600 bg-orange-900/20",
  Sales: "border-pink-600 bg-pink-900/20",
  DataAnalyst: "border-blue-600 bg-blue-900/20",
  TeamLeader: "border-indigo-600 bg-indigo-900/20",
  Engineer2: "border-teal-600 bg-teal-900/20",
};
const DEFAULT_COLOR = "border-gray-600 bg-gray-900/20";

const MAX_VISIBLE_ROLES = 5;
let agentPollTimer = null;
let visibleRoleStart = 0;
let cachedAgentRoles = [];
// Track per-role log index for incremental fetching
const roleLogIndexes = {};

async function refreshAgentPanel() {
  try {
    const res = await fetch(`${API}/api/agent-roles`);
    cachedAgentRoles = await res.json();
  } catch (_) { cachedAgentRoles = []; }

  if (cachedAgentRoles.length === 0) {
    agentEmpty.classList.remove("hidden");
    agentSlider.innerHTML = "";
    agentLogsGrid.innerHTML = "";
    return;
  }
  agentEmpty.classList.add("hidden");
  renderSlider();
  await renderAgentLogs();
}

function renderSlider() {
  agentSlider.innerHTML = "";
  cachedAgentRoles.forEach((r, i) => {
    const color = ROLE_COLORS[r.name] || DEFAULT_COLOR;
    const btn = document.createElement("button");
    btn.className = `shrink-0 px-3 py-1.5 rounded-lg border text-xs font-medium transition ${color} hover:opacity-80`;
    btn.textContent = `${r.name} (${r.log_count})`;
    btn.addEventListener("click", () => {
      visibleRoleStart = Math.max(0, i - Math.floor(MAX_VISIBLE_ROLES / 2));
      renderAgentLogs();
    });
    agentSlider.appendChild(btn);
  });
}

sliderLeft.addEventListener("click", () => {
  agentSlider.scrollBy({ left: -200, behavior: "smooth" });
});
sliderRight.addEventListener("click", () => {
  agentSlider.scrollBy({ left: 200, behavior: "smooth" });
});

async function renderAgentLogs() {
  const visible = cachedAgentRoles.slice(visibleRoleStart, visibleRoleStart + MAX_VISIBLE_ROLES);
  // Set grid columns based on visible count
  const cols = Math.min(visible.length, MAX_VISIBLE_ROLES);
  agentLogsGrid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  agentLogsGrid.innerHTML = "";

  for (const role of visible) {
    const color = ROLE_COLORS[role.name] || DEFAULT_COLOR;
    const card = document.createElement("div");
    card.className = `border rounded-lg flex flex-col overflow-hidden ${color}`;
    card.style.maxHeight = "100%";

    // Header
    const header = document.createElement("div");
    header.className = "px-3 py-2 border-b border-gray-700 flex items-center justify-between";
    header.innerHTML = `
      <span class="text-sm font-semibold">${role.name}</span>
      <span class="text-xs text-gray-500">${role.log_count} entries</span>`;
    card.appendChild(header);

    // Log content
    const logArea = document.createElement("div");
    logArea.className = "flex-1 overflow-y-auto p-2 font-mono text-xs space-y-1";
    logArea.id = `agent-log-${role.name}`;

    try {
      const afterIdx = roleLogIndexes[role.name] || 0;
      const res = await fetch(`${API}/api/agent-logs?role=${encodeURIComponent(role.name)}&after=${afterIdx}`);
      const data = await res.json();
      // Render all logs (full refresh for card rebuild)
      const allRes = await fetch(`${API}/api/agent-logs?role=${encodeURIComponent(role.name)}&after=0`);
      const allData = await allRes.json();
      roleLogIndexes[role.name] = allData.total;

      if (allData.logs.length === 0) {
        logArea.innerHTML = '<p class="text-gray-600 italic">Waiting for activity…</p>';
      } else {
        allData.logs.forEach((entry) => {
          const line = document.createElement("div");
          line.className = "text-gray-300";
          const isStart = entry.text.includes("▶");
          const isDone = entry.text.includes("✓");
          const isErr = entry.text.includes("✗");
          if (isStart) line.className = "text-blue-300";
          else if (isDone) line.className = "text-green-300";
          else if (isErr) line.className = "text-red-400";
          line.textContent = `[${entry.ts}] ${entry.text}`;
          logArea.appendChild(line);
        });
      }
    } catch (_) {
      logArea.innerHTML = '<p class="text-gray-600 italic">Error loading logs.</p>';
    }

    card.appendChild(logArea);
    agentLogsGrid.appendChild(card);

    // Auto-scroll log area to bottom
    logArea.scrollTop = logArea.scrollHeight;
  }
}

function startAgentPolling() {
  if (agentPollTimer) clearInterval(agentPollTimer);
  agentPollTimer = setInterval(async () => {
    if (!isRunning) { clearInterval(agentPollTimer); agentPollTimer = null; return; }
    // Only refresh if agent tab is visible
    if (!panelAgents.classList.contains("hidden")) {
      await refreshAgentPanel();
    }
  }, 2000);
}

// ---------------------------------------------------------------------------
// File viewer + right-click context menu
// ---------------------------------------------------------------------------

const RUNNABLE_EXTS = [".py", ".js", ".sh"];

async function loadFiles(dirPath = "") {
  try {
    const res = await fetch(`${API}/api/files?path=${encodeURIComponent(dirPath)}`);
    const data = await res.json();
    return data.entries || [];
  } catch (_) { return []; }
}

async function renderFileTree(container, dirPath = "", depth = 0) {
  const entries = await loadFiles(dirPath);
  if (entries.length === 0 && depth === 0) {
    container.innerHTML = '<p class="text-xs text-gray-600 italic">No files yet.</p>';
    return;
  }
  for (const entry of entries) {
    const row = document.createElement("div");
    row.style.paddingLeft = `${depth * 14}px`;
    if (entry.is_dir) {
      row.className = "flex items-center gap-1 cursor-pointer hover:text-blue-400 py-0.5 select-none";
      row.innerHTML = `<span class="folder-icon">📁</span><span>${entry.name}</span>`;
      let expanded = false, childContainer = null;
      row.addEventListener("click", async () => {
        if (!expanded) {
          childContainer = document.createElement("div");
          row.after(childContainer);
          await renderFileTree(childContainer, entry.path, depth + 1);
          row.querySelector(".folder-icon").textContent = "📂";
          expanded = true;
        } else {
          childContainer.remove(); childContainer = null;
          row.querySelector(".folder-icon").textContent = "📁";
          expanded = false;
        }
      });
    } else {
      const isRunnable = RUNNABLE_EXTS.some((ext) => entry.name.endsWith(ext));
      row.className = "flex items-center gap-1 cursor-pointer hover:text-blue-400 py-0.5 text-gray-400 select-none";
      row.innerHTML = `<span>📄</span><span class="truncate">${entry.name}</span>`;
      row.addEventListener("click", () => openFilePreview(entry.path));
      if (isRunnable) {
        row.addEventListener("contextmenu", (e) => { e.preventDefault(); showContextMenu(e.pageX, e.pageY, entry.path); });
      }
    }
    container.appendChild(row);
  }
}

function showContextMenu(x, y, filePath) {
  contextMenuTarget = filePath;
  ctxRun.classList.toggle("hidden", runningProjects.has(filePath));
  ctxStop.classList.toggle("hidden", !runningProjects.has(filePath));
  contextMenu.style.left = `${x}px`;
  contextMenu.style.top = `${y}px`;
  contextMenu.classList.remove("hidden");
}

document.addEventListener("click", () => contextMenu.classList.add("hidden"));

ctxRun.addEventListener("click", async () => {
  if (!contextMenuTarget) return;
  const filePath = contextMenuTarget;
  contextMenu.classList.add("hidden");
  try {
    const res = await fetch(`${API}/api/run-project`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: filePath }) });
    const data = await res.json();
    if (data.error) { appendChat(`[run] Error: ${data.error}`, "error"); return; }
    runningProjects.add(filePath);
    appendChat(`[run] Started: ${filePath} (PID ${data.pid})`, "system");
    switchTab("terminal");
    appendTerminal(`\n--- Running ${filePath} ---\n`);
    pollProjectOutput(filePath);
  } catch (err) { appendChat(`[run] Failed: ${err.message}`, "error"); }
});

ctxStop.addEventListener("click", async () => {
  if (!contextMenuTarget) return;
  const filePath = contextMenuTarget;
  contextMenu.classList.add("hidden");
  try {
    await fetch(`${API}/api/stop-project`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: filePath }) });
    runningProjects.delete(filePath);
    appendTerminal(`\n--- Stopped ${filePath} ---\n`);
    appendChat(`[run] Stopped: ${filePath}`, "system");
  } catch (err) { appendChat(`[run] Stop failed: ${err.message}`, "error"); }
});

async function pollProjectOutput(filePath) {
  while (runningProjects.has(filePath)) {
    try {
      const res = await fetch(`${API}/api/project-output?path=${encodeURIComponent(filePath)}`);
      const data = await res.json();
      if (data.output) appendTerminal(data.output);
      if (!data.running) { runningProjects.delete(filePath); appendTerminal(`\n--- ${filePath} exited ---\n`); break; }
    } catch (_) { break; }
    await new Promise((r) => setTimeout(r, 500));
  }
}

async function openFilePreview(filePath) {
  try {
    const res = await fetch(`${API}/api/file?path=${encodeURIComponent(filePath)}`);
    const data = await res.json();
    if (data.error) return;
    previewFilename.textContent = filePath;
    previewContent.textContent = data.content;
    filePreview.classList.remove("hidden");
  } catch (_) {}
}

btnClosePreview.addEventListener("click", () => filePreview.classList.add("hidden"));

async function refreshFiles() { fileTree.innerHTML = ""; await renderFileTree(fileTree); }
btnRefreshFiles.addEventListener("click", refreshFiles);

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

loadRoles();
refreshFiles();
setInterval(() => { if (isRunning) refreshFiles(); }, 15000);
