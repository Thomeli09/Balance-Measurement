# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Obect management library

# Other Lib
import copy

# Custom Lib


def ObjectCopy(Object):
    """
    Copy an object

    Get an object and return a copy of it that can 
    be modified without changing the original object
    """
    return copy.deepcopy(Object)
    