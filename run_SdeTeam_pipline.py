import asyncio
import traceback

from sdeteam.logs import logger
from sdeteam.roles import ProductManager, Architect, ProjectManager, Engineer, QaEngineer
from sdeteam.team import Team


async def main():
    logger.info("=== SdeTeam starting ===")
    team = Team(use_mgx=False)
    team.hire([
        ProductManager(use_fixed_sop=True),   # Alice: writes PRD
        Architect(use_fixed_sop=True),         # Bob: system design
        ProjectManager(use_fixed_sop=True),    # Eve: task breakdown
        Engineer(),                             # Alex: writes code
        QaEngineer(),                           # Edward: writes & runs tests
    ])
    team.invest(10.0)
    try:
        await team.run(
            n_round=50,
            idea="""
        Build a minimal Python Flask REST API todo app. Keep it to as few files as possible (ideally 3-4 files max).
        Single file app.py with: User and Todo models (SQLAlchemy + SQLite), JWT auth (register/login), CRUD for todos scoped per user.
        Plus requirements.txt. Use port 5001. Save to workspace/todo_app/.
        Do NOT create separate folders for models, routes, utils, or config. Keep everything in one app.py file.
        """,
        )
    except Exception as e:
        logger.error(f"=== SdeTeam CRASHED ===: {e}")
        logger.error(traceback.format_exc())
        raise
    logger.info("=== SdeTeam finished successfully ===")

asyncio.run(main())
