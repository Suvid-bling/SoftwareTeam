"""
Test whether the configured LLM drops the connection on Alex's actual prompt.
Sends the real ~10k token prompt through the SdeTeam LLM provider and checks for success/failure.

Usage:
    .venv/bin/python test/test_llm_connection.py
"""

import asyncio
import json
import time
import socket

from sdeteam.config2 import config
from sdeteam.context import Context
from sdeteam.environment.mgx.mgx_env import MGXEnv
from sdeteam.roles.di.engineer2 import Engineer2
from sdeteam.roles.di.team_leader import TeamLeader
from sdeteam.roles.di.data_analyst import DataAnalyst
from sdeteam.schema import UserMessage
from sdeteam.actions.di.run_command import RunCommand
from sdeteam.utils.role_zero_utils import get_plan_status
from sdeteam.provider.llm_provider_registry import create_llm_instance


async def build_alex_prompt():
    """Build the exact prompt Alex would receive in a real run."""
    ctx = Context()
    env = MGXEnv(context=ctx)
    tl, eng, da = TeamLeader(), Engineer2(), DataAnalyst()
    env.add_roles([tl, eng, da])

    task_msg = UserMessage(
        content=(
            "[Message] from Mike to Alex: Implement the full-stack TaskFlow application. "
            "Save all files to workspace/taskflow/. "
            "Backend: Python Flask REST API with JWT auth, SQLAlchemy ORM with SQLite, "
            "CRUD endpoints for Projects/Tasks/Comments/Dashboard, input validation, "
            "error handling, API rate limiting, logging with rotation. "
            "Frontend: HTML/CSS/JavaScript (no framework) with login/register, dashboard with charts, "
            "kanban board with drag-and-drop, project list/detail views, task creation/edit modal, "
            "responsive CSS Grid/Flexbox. "
            "DevOps: Dockerfile, docker-compose.yml, pytest unit tests, database migration script, "
            "README.md, requirements.txt, .env.example."
        ),
        sent_from="Mike", send_to="Alex", cause_by=RunCommand,
    )
    eng.rc.memory.add(task_msg)
    eng.planner.plan.goal = task_msg.content

    tools = await eng.tool_recommender.recommend_tools()
    tool_info = json.dumps({t.name: t.schemas for t in tools})
    plan_status, current_task = get_plan_status(planner=eng.planner)
    example = eng._retrieve_experience()
    instruction = eng.instruction.strip()

    system_prompt = eng.system_prompt.format(
        role_info=eng._get_prefix(),
        task_type_desc=eng.task_type_desc,
        available_commands=tool_info,
        example=example,
        instruction=instruction,
    )
    cmd_prompt = eng.cmd_prompt.format(
        current_state="",
        plan_status=plan_status,
        current_task=current_task,
        respond_language="English",
    )
    memory = eng.rc.memory.get(eng.memory_k)
    user_msgs = eng.llm.format_msg(memory + [UserMessage(content=cmd_prompt)])
    return [{"role": "system", "content": system_prompt}] + user_msgs


async def test_connection():
    llm_config = config.llm
    print(f"Model:    {llm_config.model}")
    print(f"API Type: {llm_config.api_type}")
    print(f"Base URL: {llm_config.base_url}")
    print(f"Stream:   {llm_config.stream}")
    print(f"Timeout:  {llm_config.timeout}s")
    print(f"Reasoning:{llm_config.reasoning}")
    print()

    # --- Test 1: Small prompt (baseline) ---
    print("=" * 50)
    print("TEST 1: Small prompt (baseline)")
    print("=" * 50)
    llm = create_llm_instance(llm_config)
    start = time.time()
    try:
        result = await llm.aask("Say hi in one word.", system_msgs=["You are helpful."])
        elapsed = time.time() - start
        print(f"  Result:  {result.strip()}")
        print(f"  Time:    {elapsed:.1f}s")
        print(f"  Status:  PASS ✓")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  Error:   {e}")
        print(f"  Time:    {elapsed:.1f}s")
        print(f"  Status:  FAIL ✗")
        return
    print()

    # --- Test 2: Alex's actual ~10k token prompt ---
    print("=" * 50)
    print("TEST 2: Alex's full prompt (~10k tokens)")
    print("=" * 50)
    messages = await build_alex_prompt()
    total_chars = sum(len(m["content"]) for m in messages)
    print(f"  Messages: {len(messages)}")
    print(f"  Chars:    {total_chars:,} (~{total_chars // 4:,} tokens)")
    print(f"  Sending...")

    llm2 = create_llm_instance(llm_config)
    start = time.time()
    try:
        # Use the same path as _think() -> aask() -> acompletion_text()
        system_msg = messages[0]["content"]
        user_msgs = messages[1:]
        result = await llm2.acompletion_text(messages, stream=llm_config.stream, timeout=llm_config.timeout)
        elapsed = time.time() - start
        print(f"  Time:    {elapsed:.1f}s")
        print(f"  Length:  {len(result)} chars")
        print(f"  Preview: {result[:200]}...")
        print(f"  Status:  PASS ✓")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  Error:   {type(e).__name__}: {e}")
        print(f"  Time:    {elapsed:.1f}s")
        print(f"  Status:  FAIL ✗ — LLM dropped the connection")

    # --- Test 3: Check TCP state after call ---
    print()
    print("=" * 50)
    print("TEST 3: TCP connection state")
    print("=" * 50)
    import os
    pid = os.getpid()
    os.system(f"lsof -i -P -n 2>/dev/null | grep {pid} | grep -v LISTEN || echo '  No active connections (clean)'")


if __name__ == "__main__":
    asyncio.run(test_connection())
