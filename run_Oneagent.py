import asyncio
from sdeteam.roles.di.data_interpreter import DataInterpreter

async def main():
    di = DataInterpreter()
    await di.run("""
    Build a command-line expense tracker app in Python. 
    Create these separate files in workspace/expense_tracker/:
    1. models.py - Expense and Category dataclasses with validation
    2. database.py - SQLite storage layer (CRUD operations)  
    3. cli.py - argparse CLI with add/list/summary/export commands
    4. main.py - entry point that wires everything together
    Support CSV export and monthly summary reports with colored output.
    Save all files to workspace/expense_tracker/
    """)

asyncio.run(main())
