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
        # Architect(),       # design & review
        # QaEngineer(),      # testing
    ])
    team.invest(10.0)
    try:
        await team.run(
            n_round=100000,
            idea="""
        Write comprehensive tests for the Flask login application at workspace/login_app/.
        Tasks:
        1. Create a tests/ folder under workspace/login_app/
        2. Write test files in workspace/login_app/tests/:
        - test_auth.py: Test user registration and login endpoints
        - test_models.py: Test User model and database operations
        3. Tests should cover:
        - User signup with valid/invalid data
        - User login with correct/incorrect credentials
        - Successful login redirect to success page
        - Password hashing verification
        4. Use pytest framework
        5. Run all tests and report results
        """,
        )
    except Exception as e:
        logger.error(f"=== SdeTeam CRASHED ===: {e}")
        logger.error(traceback.format_exc())
        raise
    logger.info("=== SdeTeam finished successfully ===")

asyncio.run(main())