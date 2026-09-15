# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Test the logging functionality of the module

# Other Lib


# Custom Lib
from GUIMessageLib import LogManager

"""
# Improvement to be done:
- 
"""

Msg = LogManager(Name="ScaleApp", LogFile="scale_app.log")

Msg.getLevel = 0

Msg.LoggerConfiguration()

Something = 50

Msg.Debug(Message=f"Test debug {Something}")
Msg.Info(Message=f"Test information {Something}")
Msg.Warning(Message=f"Test warning {Something}")
Msg.Error(Message=f"Test error {Something}")
Msg.Critical(Message=f"Test critical {Something}")
Msg.Exception(Message=f"Test exception {Something}")

Msg.Shutdown()