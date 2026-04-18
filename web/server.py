"""
SdeTeam Web Frontend — FastAPI backend
Provides REST + WebSocket interface to the Team engine.
"""

import asyncio
import json
import os
import subprocess
import signal
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from sdeteam.logs import logger
from sdeteam.roles import (
    ProductManager, Architect, ProjectManager,
    Engineer, QaEngineer, Searcher, Sales,
    DataAnalyst, TeamLeader, Engineer2,
)
from sdeteam.team import Team

app = FastAPI(title="SdeTeam Web UI")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
team_instance: Optional[Team] = None
team_task: Optional[asyncio.Task] = None
run_logs: list[str] = []

# Available roles registry
ROLE_REGISTRY = {
    "ProductManager": {"cls": ProductManager, "kwargs": {"use_fixed_sop": True}, "desc": "Alice — writes PRD"},
    "Architect":      {"cls": Architect,       "kwargs": {"use_fixed_sop": True}, "desc": "Bob — system design"},
    "ProjectManager": {"cls": ProjectManager,  "kwargs": {"use_fixed_sop": True}, "desc": "Eve — task breakdown"},
    "Engineer":       {"cls": Engineer,         "kwargs": {},                      "desc": "Alex — writes code"},
    "QaEngineer":     {"cls": QaEngineer,       "kwargs": {},                      "desc": "Edward — writes & runs tests"},
    "Searcher":       {"cls": Searcher,         "kwargs": {},                      "desc": "Searcher — web research"},
    "Sales":          {"cls": Sales,            "kwargs": {},                      "desc": "Sales — customer facing"},
    "DataAnalyst":    {"cls": DataAnalyst,      "kwargs": {},                      "desc": "DataAnalyst — data analysis"},
    "TeamLeader":     {"cls": TeamLeader,       "kwargs": {},                      "desc": "TeamLeader — leads DI team"},
    "Engineer2":      {"cls": Engineer2,        "kwargs": {},                      "desc": "Engineer2 — DI engineer"},
}

WORKSPACE_ROOT = Path("workspace")

# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def index():
    return FileResponse("web/static/index.html")


@app.get("/api/roles")
async def list_roles():
    """Return available roles for hiring."""
    return [{"name": k, "desc": v["desc"]} for k, v in ROLE_REGISTRY.items()]


@app.get("/api/status")
async def status():
    """Return current team run status."""
    running = team_task is not None and not team_task.done()
    return {"running": running, "log_count": len(run_logs)}


@app.get("/api/logs")
async def get_logs(after: int = 0):
    """Return logs after a given index (for polling)."""
    return {"logs": run_logs[after:], "total": len(run_logs)}


class RunRequest(BaseModel):
    idea: str
    roles: list[str]
    investment: float = 10.0
    n_round: int = 100


@app.post("/api/run")
async def run_team(req: RunRequest):
    """Start a team run with the given idea and hired roles."""
    global team_instance, team_task, run_logs

    if team_task and not team_task.done():
        return JSONResponse({"error": "A run is already in progress."}, status_code=409)

    run_logs.clear()

    # Build role instances
    hired = []
    for role_name in req.roles:
        entry = ROLE_REGISTRY.get(role_name)
        if entry:
            hired.append(entry["cls"](**entry["kwargs"]))

    if not hired:
        return JSONResponse({"error": "No valid roles selected."}, status_code=400)

    team_instance = Team(use_mgx=False)
    team_instance.hire(hired)
    team_instance.invest(req.investment)

    async def _run():
        try:
            run_logs.append("[system] Team run started.")
            await team_instance.run(n_round=req.n_round, idea=req.idea)
            run_logs.append("[system] Team run finished successfully.")
        except Exception as e:
            run_logs.append(f"[error] {e}")
            run_logs.append(traceback.format_exc())

    team_task = asyncio.create_task(_run())
    return {"status": "started"}


@app.post("/api/stop")
async def stop_team():
    """Cancel the running team task."""
    global team_task
    if team_task and not team_task.done():
        team_task.cancel()
        run_logs.append("[system] Run cancelled by user.")
        return {"status": "cancelled"}
    return {"status": "not_running"}


# ---------------------------------------------------------------------------
# File viewer — mirrors workspace directory
# ---------------------------------------------------------------------------

@app.get("/api/files")
async def list_files(path: str = ""):
    """List files/dirs under workspace root."""
    target = WORKSPACE_ROOT / path
    if not target.exists():
        return {"entries": [], "path": path}

    entries = []
    try:
        for item in sorted(target.iterdir()):
            if item.name.startswith("."):
                continue
            entries.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None,
                "path": str(item.relative_to(WORKSPACE_ROOT)),
            })
    except PermissionError:
        pass
    return {"entries": entries, "path": path}


@app.get("/api/file")
async def read_file(path: str):
    """Read a single file's content."""
    target = WORKSPACE_ROOT / path
    if not target.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)
    try:
        content = target.read_text(errors="replace")
        return {"path": path, "content": content}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# WebSocket for real-time log streaming
# ---------------------------------------------------------------------------

@app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket):
    await ws.accept()
    idx = 0
    try:
        while True:
            if idx < len(run_logs):
                for line in run_logs[idx:]:
                    await ws.send_text(line)
                idx = len(run_logs)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass


# ---------------------------------------------------------------------------
# Terminal — interactive shell via WebSocket
# ---------------------------------------------------------------------------

@app.websocket("/ws/terminal")
async def ws_terminal(ws: WebSocket):
    await ws.accept()
    proc = await asyncio.create_subprocess_exec(
        "/bin/bash", "-i",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(WORKSPACE_ROOT),
        env={**os.environ, "TERM": "dumb", "PS1": "$ "},
    )

    async def _read_stdout():
        try:
            while True:
                chunk = await proc.stdout.read(4096)
                if not chunk:
                    break
                await ws.send_text(chunk.decode(errors="replace"))
        except (WebSocketDisconnect, ConnectionError):
            pass

    reader_task = asyncio.create_task(_read_stdout())

    try:
        while True:
            data = await ws.receive_text()
            if proc.stdin:
                proc.stdin.write(data.encode())
                await proc.stdin.drain()
    except WebSocketDisconnect:
        pass
    finally:
        proc.kill()
        reader_task.cancel()


# ---------------------------------------------------------------------------
# Run project — execute a file inside workspace
# ---------------------------------------------------------------------------

# Track running project processes
project_processes: dict[str, asyncio.subprocess.Process] = {}


class RunProjectRequest(BaseModel):
    path: str  # relative to workspace root, e.g. "todo_app/app.py"


@app.post("/api/run-project")
async def run_project(req: RunProjectRequest):
    """Run a Python file from the workspace."""
    target = (WORKSPACE_ROOT / req.path).resolve()
    if not target.is_file():
        return JSONResponse({"error": "File not found"}, status_code=404)

    # Determine how to run based on extension
    ext = target.suffix.lower()
    if ext == ".py":
        cmd = ["python3", str(target)]
    elif ext == ".js":
        cmd = ["node", str(target)]
    elif ext == ".sh":
        cmd = ["bash", str(target)]
    else:
        return JSONResponse({"error": f"Unsupported file type: {ext}"}, status_code=400)

    # Kill previous process for same path if still running
    if req.path in project_processes:
        old = project_processes[req.path]
        if old.returncode is None:
            old.kill()

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(target.parent),
    )
    project_processes[req.path] = proc
    return {"status": "started", "pid": proc.pid, "path": req.path}


@app.get("/api/project-output")
async def project_output(path: str):
    """Read output from a running project process."""
    proc = project_processes.get(path)
    if not proc:
        return {"output": "", "running": False}
    running = proc.returncode is None
    output = ""
    if proc.stdout:
        try:
            chunk = await asyncio.wait_for(proc.stdout.read(8192), timeout=0.5)
            output = chunk.decode(errors="replace")
        except asyncio.TimeoutError:
            pass
    return {"output": output, "running": running}


@app.post("/api/stop-project")
async def stop_project(req: RunProjectRequest):
    """Stop a running project process."""
    proc = project_processes.get(req.path)
    if proc and proc.returncode is None:
        proc.kill()
        return {"status": "killed"}
    return {"status": "not_running"}


# Serve static files last (catch-all)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
