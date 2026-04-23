import asyncio
import traceback

from sdeteam.logs import logger
from sdeteam.roles.di.team_leader import TeamLeader
from sdeteam.roles.di.engineer2 import Engineer2
from sdeteam.roles.architect import Architect
from sdeteam.roles.test_engineer import TestEngineer
from sdeteam.roles.reviewer import Reviewer

from sdeteam.team import Team


async def main():
    logger.info("=== SdeTeam starting ===")
    team = Team()
    team.env.is_public_chat = False  # prevent broadcast, use direct routing only
    team.hire([
        TeamLeader(),
        Architect(),
        Engineer2(),       # coding
        TestEngineer(),    # testing (DI mode)
        Reviewer(),         # code review (DI mode)
    ])
    team.invest(10.0)
    try:
        await team.run(
            n_round=100000,
            idea="""
请对 2048_game 项目进行代码审查。和测试

项目路径: 2048_game/

        """,
        )
    except Exception as e:
        logger.error(f"=== SdeTeam CRASHED ===: {e}")
        logger.error(traceback.format_exc())
        raise
    logger.info("=== SdeTeam finished successfully ===")

asyncio.run(main())