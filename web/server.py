"""
SdeTeam Web Frontend — FastAPI backend
Provides REST + WebSocket interface to the Team engine.
"""

import asyncio
import json
import os
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


# Serve static files last (catch-all)
app.mount("/static", StaticFiles(directory="web/static"), name="static")
