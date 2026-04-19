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
        Create a simple login page with sign-up and sign-in functionality.
        - A registration form (sign up) with username and password fields
        - A login form (sign in) with username and password fields
        - If login is successful, redirect to a Success page that says "Login Successful!"
        - Use HTML/CSS/JavaScript for the frontend
        - Use a simple backend (Python Flask) to handle authentication
        - Store users in SQLite for simplicity
        - Save all files to login_app/
        """,
        )
    except Exception as e:
        logger.error(f"=== SdeTeam CRASHED ===: {e}")
        logger.error(traceback.format_exc())
        raise
    logger.info("=== SdeTeam finished successfully ===")

asyncio.run(main())