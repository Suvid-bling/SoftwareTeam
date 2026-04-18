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
const panelChat = document.getElementById("panel-chat");
const panelTerminal = document.getElementById("panel-terminal");
const terminalOutput = document.getElementById("terminal-output");
const terminalInput = document.getElementById("terminal-input");
const btnSendCmd = document.getElementById("btn-send-cmd");

// Context menu refs
const contextMenu = document.getElementById("context-menu");
const ctxRun = document.getElementById("ctx-run");
const ctxStop = document.getElementById("ctx-stop");
let contextMenuTarget = null; // file path for right-click
const runningProjects = new Set();

// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------

function switchTab(tab) {
  const isChat = tab === "chat";
  tabChat.classList.toggle("active", isChat);
  tabChat.classList.toggle("border-blue-500", isChat);
  tabChat.classList.toggle("text-blue-400", isChat);
  tabChat.classList.toggle("border-transparent", !isChat);
  tabChat.classList.toggle("text-gray-500", !isChat);

  tabTerminal.classList.toggle("active", !isChat);
  tabTerminal.classList.toggle("border-blue-500", !isChat);
  tabTerminal.classList.toggle("text-blue-400", !isChat);
  tabTerminal.classList.toggle("border-transparent", isChat);
  tabTerminal.classList.toggle("text-gray-500", isChat);

  panelChat.classList.toggle("hidden", !isChat);
  panelTerminal.classList.toggle("hidden", isChat);

  if (!isChat && !termWs) connectTerminal();
}

tabChat.addEventListener("click", () => switchTab("chat"));
tabTerminal.addEventListener("click", () => switchTab("terminal"));

// ---------------------------------------------------------------------------
// Terminal WebSocket
// ---------------------------------------------------------------------------

function connectTerminal() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  termWs = new WebSocket(`${proto}//${location.host}/ws/terminal`);

  termWs.onopen = () => {
    terminalOutput.textContent = "";
    appendTerminal("Connected to workspace shell.\n");
  };

  termWs.onmessage = (e) => {
    appendTerminal(e.data);
  };

  termWs.onclose = () => {
    appendTerminal("\n[disconnected]\n");
    termWs = null;
  };
}

function appendTerminal(text) {
  terminalOutput.textContent += text;
  terminalOutput.scrollTop = terminalOutput.scrollHeight;
}

function sendTerminalCommand() {
  const cmd = terminalInput.value;
  if (!cmd && !termWs) return;
  if (termWs && termWs.readyState === WebSocket.OPEN) {
    termWs.send(cmd + "\n");
    terminalInput.value = "";
  }
}

btnSendCmd.addEventListener("click", sendTerminalCommand);
terminalInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendTerminalCommand();
  }
});

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
  if (type === "user") {
    div.className = "bg-blue-900/40 border border-blue-800 rounded-lg px-3 py-2 text-blue-200 whitespace-pre-wrap";
  } else if (type === "error") {
    div.className = "text-red-400 whitespace-pre-wrap";
  } else if (type === "system") {
    div.className = "text-green-400 whitespace-pre-wrap";
  } else {
    div.className = "text-gray-400 whitespace-pre-wrap";
  }
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
  if (selectedRoles.size === 0) {
    appendChat("Please select at least one role.", "error");
    return;
  }
  appendChat(idea, "user");
  ideaInput.value = "";
  const body = {
    idea,
    roles: [...selectedRoles],
    investment: parseFloat(investmentInput.value) || 10,
    n_round: 100,
  };
  try {
    const res = await fetch(`${API}/api/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (data.error) { appendChat(data.error, "error"); return; }
    setRunning(true);
    connectWS();
  } catch (err) {
    appendChat(`Failed to start: ${err.message}`, "error");
  }
});

btnStop.addEventListener("click", async () => {
  try {
    await fetch(`${API}/api/stop`, { method: "POST" });
    appendChat("Stop requested.", "system");
  } catch (err) {
    appendChat(`Stop failed: ${err.message}`, "error");
  }
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
    if (line.startsWith("[error]")) {
      appendChat(line, "error");
    } else if (line.startsWith("[system]")) {
      appendChat(line, "system");
      if (line.includes("finished") || line.includes("cancelled")) {
        setRunning(false);
        refreshFiles();
      }
    } else {
      appendChat(line, "log");
    }
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
      let expanded = false;
      let childContainer = null;
      row.addEventListener("click", async () => {
        if (!expanded) {
          childContainer = document.createElement("div");
          row.after(childContainer);
          await renderFileTree(childContainer, entry.path, depth + 1);
          row.querySelector(".folder-icon").textContent = "📂";
          expanded = true;
        } else {
          childContainer.remove();
          childContainer = null;
          row.querySelector(".folder-icon").textContent = "📁";
          expanded = false;
        }
      });
    } else {
      const isRunnable = RUNNABLE_EXTS.some((ext) => entry.name.endsWith(ext));
      row.className = "flex items-center gap-1 cursor-pointer hover:text-blue-400 py-0.5 text-gray-400 select-none";
      row.innerHTML = `<span>📄</span><span class="truncate">${entry.name}</span>`;
      row.addEventListener("click", () => openFilePreview(entry.path));

      // Right-click for runnable files
      if (isRunnable) {
        row.addEventListener("contextmenu", (e) => {
          e.preventDefault();
          showContextMenu(e.pageX, e.pageY, entry.path);
        });
      }
    }
    container.appendChild(row);
  }
}

function showContextMenu(x, y, filePath) {
  contextMenuTarget = filePath;
  const isProjectRunning = runningProjects.has(filePath);
  ctxRun.classList.toggle("hidden", isProjectRunning);
  ctxStop.classList.toggle("hidden", !isProjectRunning);
  contextMenu.style.left = `${x}px`;
  contextMenu.style.top = `${y}px`;
  contextMenu.classList.remove("hidden");
}

// Hide context menu on click anywhere
document.addEventListener("click", () => {
  contextMenu.classList.add("hidden");
});

// Run file from context menu
ctxRun.addEventListener("click", async () => {
  if (!contextMenuTarget) return;
  const filePath = contextMenuTarget;
  contextMenu.classList.add("hidden");

  try {
    const res = await fetch(`${API}/api/run-project`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: filePath }),
    });
    const data = await res.json();
    if (data.error) {
      appendChat(`[run] Error: ${data.error}`, "error");
      return;
    }
    runningProjects.add(filePath);
    appendChat(`[run] Started: ${filePath} (PID ${data.pid})`, "system");

    // Switch to terminal and stream output
    switchTab("terminal");
    appendTerminal(`\n--- Running ${filePath} ---\n`);
    pollProjectOutput(filePath);
  } catch (err) {
    appendChat(`[run] Failed: ${err.message}`, "error");
  }
});

// Stop file from context menu
ctxStop.addEventListener("click", async () => {
  if (!contextMenuTarget) return;
  const filePath = contextMenuTarget;
  contextMenu.classList.add("hidden");

  try {
    await fetch(`${API}/api/stop-project`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: filePath }),
    });
    runningProjects.delete(filePath);
    appendTerminal(`\n--- Stopped ${filePath} ---\n`);
    appendChat(`[run] Stopped: ${filePath}`, "system");
  } catch (err) {
    appendChat(`[run] Stop failed: ${err.message}`, "error");
  }
});

async function pollProjectOutput(filePath) {
  while (runningProjects.has(filePath)) {
    try {
      const res = await fetch(`${API}/api/project-output?path=${encodeURIComponent(filePath)}`);
      const data = await res.json();
      if (data.output) appendTerminal(data.output);
      if (!data.running) {
        runningProjects.delete(filePath);
        appendTerminal(`\n--- ${filePath} exited ---\n`);
        break;
      }
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

async function refreshFiles() {
  fileTree.innerHTML = "";
  await renderFileTree(fileTree);
}

btnRefreshFiles.addEventListener("click", refreshFiles);

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

loadRoles();
refreshFiles();
setInterval(() => { if (isRunning) refreshFiles(); }, 15000);
