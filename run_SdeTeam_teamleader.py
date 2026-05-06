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
        TeamLeader(), #协调智能体
        Architect(),  #规划智能体
        Engineer2(),  #开发智能体    
        TestEngineer(),   #测试智能体
        Reviewer(),       #代码审查智能体
    ])
    team.invest(10.0)
    try:
        await team.run(
            n_round=100000,
            idea="""
创建一个Python计算器程序，支持加减乘除。
项目目录：calc/
        """,
        )
    except Exception as e:
        logger.error(f"=== SdeTeam CRASHED ===: {e}")
        logger.error(traceback.format_exc())
        raise
    logger.info("=== SdeTeam finished successfully ===")

asyncio.run(main())