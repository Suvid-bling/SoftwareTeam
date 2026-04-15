#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/    : 2023/5/12 10:23
/
@File    : test_project_manager.py
"""
import pytest

from sdeteam.logs import logger
from sdeteam.roles import ProjectManager
from tests.metagpt.roles.mock import MockMessages


@pytest.mark.asyncio
async def test_project_manager(context):
    project_manager = ProjectManager(context=context)
    rsp = await project_manager.run(MockMessages.tasks)
    logger.info(rsp)
