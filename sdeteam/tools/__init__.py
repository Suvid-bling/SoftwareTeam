#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdeteam.tools import libs  # this registers all tools
from sdeteam.tools.tool_registry import TOOL_REGISTRY
from sdeteam.configs.search_config import SearchEngineType
from sdeteam.configs.browser_config import WebBrowserEngineType


_ = libs, TOOL_REGISTRY  # Avoid pre-commit error


class SearchInterface:
    async def asearch(self, *args, **kwargs):
        ...


__all__ = ["SearchEngineType", "WebBrowserEngineType", "TOOL_REGISTRY"]
