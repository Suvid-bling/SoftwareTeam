#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   :

from sdeteam.ext.werewolf.actions.werewolf_actions import Hunt, Impersonate
from sdeteam.ext.werewolf.actions.guard_actions import Protect
from sdeteam.ext.werewolf.actions.seer_actions import Verify
from sdeteam.ext.werewolf.actions.witch_actions import Save, Poison
from sdeteam.ext.werewolf.actions.common_actions import Speak, NighttimeWhispers, Reflect
from sdeteam.ext.werewolf.actions.experience_operation import AddNewExperiences, RetrieveExperiences
from sdeteam.ext.werewolf.actions.moderator_actions import InstructSpeak

ACTIONS = {
    "Speak": Speak,
    "Hunt": Hunt,
    "Protect": Protect,
    "Verify": Verify,
    "Save": Save,
    "Poison": Poison,
    "Impersonate": Impersonate,
}

__all__ = ["NighttimeWhispers", "Reflect", "AddNewExperiences", "RetrieveExperiences", "InstructSpeak"]
