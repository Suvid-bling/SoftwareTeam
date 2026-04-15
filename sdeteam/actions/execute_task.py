#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdeteam.actions import Action
from sdeteam.schema import Message


class ExecuteTask(Action):
    name: str = "ExecuteTask"
    i_context: list[Message] = []

    async def run(self, *args, **kwargs):
        pass
