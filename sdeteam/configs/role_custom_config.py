#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sdeteam.configs.llm_config import LLMConfig
from sdeteam.utils.yaml_model import YamlModel


class RoleCustomConfig(YamlModel):
    """custom config for roles
    role: role's className or role's role_id
    To be expanded
    """

    role: str = ""
    llm: LLMConfig
