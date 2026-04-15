#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : unittest of team

from sdeteam.roles.project_manager import ProjectManager
from sdeteam.team import Team


def test_team():
    company = Team()
    company.hire([ProjectManager()])

    assert len(company.env.roles) == 1
