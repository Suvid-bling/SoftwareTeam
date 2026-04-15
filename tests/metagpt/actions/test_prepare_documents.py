#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
/    : 2023/12/6
@Author  : mashenquan
@File    : test_prepare_documents.py
@Desc: Unit test for prepare_documents.py
"""
import pytest

from sdeteam.actions.prepare_documents import PrepareDocuments
from sdeteam.const import REQUIREMENT_FILENAME
from sdeteam.context import Context
from sdeteam.schema import Message


@pytest.mark.asyncio
async def test_prepare_documents():
    msg = Message(content="New user requirements balabala...")
    context = Context()

    await PrepareDocuments(context=context).run(with_messages=[msg])
    assert context.git_repo
    assert context.repo
    doc = await context.repo.docs.get(filename=REQUIREMENT_FILENAME)
    assert doc
    assert doc.content == msg.content
