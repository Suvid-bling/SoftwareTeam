#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/    : 2023/5/20 14:37
/
@File    : test_architect.py
@Modified By: mashenquan, 2023-11-1. In accordance with Chapter 2.2.1 and 2.2.2 of RFC 116, utilize the new message
        distribution feature for message handling.
"""
import uuid
from pathlib import Path

import pytest

from sdeteam.actions import WritePRD
from sdeteam.actions.di.run_command import RunCommand
from sdeteam.const import PRDS_FILE_REPO
from sdeteam.logs import logger
from sdeteam.roles import Architect
from sdeteam.schema import Message
from sdeteam.utils.common import any_to_str, awrite
from tests.metagpt.roles.mock import MockMessages


@pytest.mark.asyncio
async def test_architect(context):
    # Prerequisites
    filename = uuid.uuid4().hex + ".json"
    await awrite(Path(context.config.project_path) / PRDS_FILE_REPO / filename, data=MockMessages.prd.content)

    role = Architect(context=context)
    rsp = await role.run(with_message=Message(content="", cause_by=WritePRD))
    logger.info(rsp)
    assert len(rsp.content) > 0
    assert rsp.cause_by == any_to_str(RunCommand)

    # test update
    rsp = await role.run(with_message=Message(content="", cause_by=WritePRD))
    assert rsp
    assert rsp.cause_by == any_to_str(RunCommand)
    assert len(rsp.content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
