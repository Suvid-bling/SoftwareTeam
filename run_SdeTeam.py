import asyncio
import traceback

from sdeteam.logs import logger
from sdeteam.roles.di.team_leader import TeamLeader
from sdeteam.roles.di.engineer2 import Engineer2
from sdeteam.roles.architect import Architect
from sdeteam.roles.qa_engineer import QaEngineer

from sdeteam.team import Team


async def main():
    logger.info("=== SdeTeam starting ===")
    team = Team()
    team.env.is_public_chat = False  # prevent broadcast, use direct routing only
    team.hire([
        TeamLeader(),
        Engineer2(),       # coding
        #Architect(),       # design & review
        QaEngineer(),      # testing
    ])
    team.invest(10.0)
    try:
        await team.run(
            n_round=100000,
            idea="""
        Review the existing accounting system in accounting_system/.
        - Architect: review the code architecture, identify design issues and suggest improvements
        - Engineer: fix any bugs or issues found during review
        - QA: write and run tests for all API endpoints, fix any failing tests
        All files are in workspace/accounting_system/
        """,
        )
    except Exception as e:
        logger.error(f"=== SdeTeam CRASHED ===: {e}")
        logger.error(traceback.format_exc())
        raise
    logger.info("=== SdeTeam finished successfully ===")

asyncio.run(main())
