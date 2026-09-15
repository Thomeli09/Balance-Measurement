# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Library of message management functions for balance measurement module

"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
"""
# Other Lib
import rich

import logging
from logging.handlers import RotatingFileHandler

import tkinter as tk
from tkinter import messagebox

from pathlib import Path
# Custom Lib
from ObjectManagementLib import ObjectCopy

"""
Message Management objects

# Improvement to be done:
-
"""
class LogManager:
    """
    Small abstraction layer around the logging system.

    Other classes should use this object instead of importing logging directly.
    This makes it easier to switch to another logging backend later.
    """
    def __init__(self, Name: str = "App", LogFile: str | Path = "App.log", Level: int = logging.DEBUG,
                 MaxBytes: int = 5_000_000, BackupCount: int = 5, BConsole: bool = True, BRecord: bool = True) -> None:
        # Metadata
        self._Name = Name
        
        # Parameters of the recording management
        self._BRecord = BRecord
        self._LogFile = Path(LogFile)
        self._MaxBytes = MaxBytes
        self._BackupCount = BackupCount

        # Parameters of the streaming management
        self._BConsole = BConsole

        # Parameters of the message management
        self._Level = Level
        
        # Logger configuration
        self._Logger = logging.getLogger(self._Name)
        self._BLoggerStart = False 

        # Influence on the program excecution
        self._BLocking = False # Boolean to indicate if the excecution of the program should be blocked until the message is closed

        # Others data
        self._CurrentID = 0 # Current ID of the message being managed
        self._TimeOBJ = None # Time object to manage the time of the messages
        # Configure the logger

    # Metadata
    @property
    def getName(self) -> str:
        return self._Name

    @getName.setter
    def getName(self, Name: str) -> None:
        self._Name = Name
        
    # Parameters of the recording management
    @property
    def getBRecord(self) -> bool:
        return self._BRecord

    @getBRecord.setter
    def getBRecord(self, BRecord: bool) -> None:
        self._BRecord = BRecord

    @property
    def getLogFile(self) -> Path:
        return self._LogFile

    @getLogFile.setter
    def getLogFile(self, LogFile: str | Path) -> None:
        self._LogFile = Path(LogFile)

    @property
    def getMaxBytes(self) -> int:
        return self._MaxBytes

    @getMaxBytes.setter
    def getMaxBytes(self, MaxBytes: int) -> None:
        self._MaxBytes = MaxBytes

    @property
    def getBackupCount(self) -> int:
        return self._BackupCount

    @getBackupCount.setter
    def getBackupCount(self, BackupCount: int) -> None:
        self._BackupCount = BackupCount

    # Parameters of the streaming management
    @property
    def getBConsole(self) -> bool:
        return self._BConsole

    @getBConsole.setter
    def getBConsole(self, BConsole: bool) -> None:
        self._BConsole = BConsole

    # Parameters of the message management
    @property
    def getLevel(self) -> int:
        return self._Level

    @getLevel.setter
    def getLevel(self, Level: int | str) -> None:
        if isinstance(Level, str):
            Level = Level.upper()
            if Level == "DEBUG":
                self._Level = logging.DEBUG
            elif Level == "INFO":
                self._Level = logging.INFO
            elif Level == "WARNING":
                self._Level = logging.WARNING
            elif Level == "ERROR":
                self._Level = logging.ERROR
            elif Level == "CRITICAL":
                self._Level = logging.CRITICAL
            else:
                self._Level = logging.DEBUG
        elif isinstance(Level, int):
            if Level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
                self._Level = Level
            else:
                self._Level = logging.DEBUG
    
    # Logger configuration
    @property
    def getLogger(self) -> logging.Logger:
        return self._Logger

    @getLogger.setter
    def getLogger(self, Logger: logging.Logger) -> None:
        self._Logger = Logger

    @property
    def getBLoggerStart(self) -> bool:
        return self._BLoggerStart

    @getBLoggerStart.setter
    def getBLoggerStart(self, BLoggerStart: bool) -> None:
        self._BLoggerStart = BLoggerStart

    # Influence on the program excecution
    @property
    def getBLocking(self) -> bool:
        return self._BLocking

    @getBLocking.setter
    def getBLocking(self, BLocking: bool) -> None:
        self._BLocking = BLocking

    # Others data
    @property
    def getCurrentID(self) -> int:
        return self._CurrentID

    @getCurrentID.setter
    def getCurrentID(self, CurrentID: int) -> None:
        self._CurrentID = CurrentID

    @property
    def getTimeOBJ(self):
        return self._TimeOBJ

    @getTimeOBJ.setter
    def getTimeOBJ(self, TimeOBJ) -> None:
        self._TimeOBJ = TimeOBJ

    # Configuration Methods
    def LoggerConfiguration(self, BForceReconfigure: bool = True, BOverWrite: bool = True) -> None:
        """
        Configure the internal logger.

        This method avoids adding duplicate handlers if the MessageManager
        is initialized several times.
        """

        # Set the logger level to save all messages, and let the handlers filter them
        self.getLogger.setLevel(self.getLevel)

        # Disable propagation to avoid duplicate messages in the root logger (received by other subloggers)
        self.getLogger.propagate = False

         # Check if the logger already has handlers to avoid adding duplicates
        if self.getLogger.handlers:
            if BForceReconfigure:
                for Handler in self.getLogger.handlers[:]:
                    Handler.close()
                    self.getLogger.removeHandler(Handler)
            else:
                self.getBLoggerStart = True
                return

        # Create a formatter for the log messages
        Formatter = logging.Formatter(fmt="{asctime} & {levelname:<10} & {name} & {message} & {funcName} & line {lineno}", style="{")

        # Create a rotating file handler to write log messages to a file
        if self.getBRecord:
            if BOverWrite and self.getLogFile.exists():
                self.getLogFile.unlink()

            FileHandler = RotatingFileHandler(filename=self.getLogFile, mode="w", maxBytes=self.getMaxBytes,
                backupCount=self.getBackupCount, encoding="utf-8") # mode="a" if you want to append to the log file instead of overwriting it

            FileHandler.setLevel(self.getLevel)

            FileHandler.setFormatter(Formatter)

            self.getLogger.addHandler(FileHandler)

        if self.getBConsole:
            ConsoleHandler = logging.StreamHandler()

            ConsoleHandler.setLevel(logging.INFO)

            ConsoleHandler.setFormatter(Formatter)

            self.getLogger.addHandler(ConsoleHandler)

        self.getBLoggerStart = True

    # Close the logger and release resources
    def Shutdown(self) -> None:
        logging.shutdown()

    # Data Management Methods


    # Basic message functions
    # Debug message functions
    def Debug(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.debug(Message, *args, stacklevel=2)

    # Information message functions
    def Info(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.info(Message, *args, stacklevel=2)

    # Warning message functions
    def Warning(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.warning(Message, *args, stacklevel=2)

    # Error message functions
    def Error(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.error(Message, *args, stacklevel=2)

    def Critical(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.critical(Message, *args, stacklevel=2)

    def Exception(self, Message: str, BLocking: bool = False, *args: object) -> None:
        """
        Log an exception with the full traceback.

        Use this method only inside an except block.
        """
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.exception(Message, *args, stacklevel=2)
    
class MessageManager:
    """
    Small abstraction layer around the logging system.

    Other classes should use this object instead of importing logging directly.
    This makes it easier to switch to another logging backend later.
    """
    def __init__(self, Name: str = "App", LogFile: str | Path = "App.log", Level: int = logging.DEBUG,
                 MaxBytes: int = 5_000_000, BackupCount: int = 5, BConsole: bool = True, BRecord: bool = True) -> None:
        # Metadata
        self._Name = Name
        
        # Parameters of the recording management
        self._BRecord = BRecord
        self._LogFile = Path(LogFile)
        self._MaxBytes = MaxBytes
        self._BackupCount = BackupCount

        # Parameters of the streaming management
        self._BConsole = BConsole

        # Parameters of the message management
        self._Level = Level
        
        # Logger configuration
        self._Logger = logging.getLogger(self._Name)
        self._BLoggerStart = False 

        # Influence on the program excecution
        self._BLocking = False # Boolean to indicate if the excecution of the program should be blocked until the message is closed

        # Others data
        self._CurrentID = 0 # Current ID of the message being managed
        self._TimeOBJ = None # Time object to manage the time of the messages
        # Configure the logger

    # Metadata
    @property
    def getName(self) -> str:
        return self._Name

    @getName.setter
    def getName(self, Name: str) -> None:
        self._Name = Name
        
    # Parameters of the recording management
    @property
    def getBRecord(self) -> bool:
        return self._BRecord

    @getBRecord.setter
    def getBRecord(self, BRecord: bool) -> None:
        self._BRecord = BRecord

    @property
    def getLogFile(self) -> Path:
        return self._LogFile

    @getLogFile.setter
    def getLogFile(self, LogFile: str | Path) -> None:
        self._LogFile = Path(LogFile)

    @property
    def getMaxBytes(self) -> int:
        return self._MaxBytes

    @getMaxBytes.setter
    def getMaxBytes(self, MaxBytes: int) -> None:
        self._MaxBytes = MaxBytes

    @property
    def getBackupCount(self) -> int:
        return self._BackupCount

    @getBackupCount.setter
    def getBackupCount(self, BackupCount: int) -> None:
        self._BackupCount = BackupCount

    # Parameters of the streaming management
    @property
    def getBConsole(self) -> bool:
        return self._BConsole

    @getBConsole.setter
    def getBConsole(self, BConsole: bool) -> None:
        self._BConsole = BConsole

    # Parameters of the message management
    @property
    def getLevel(self) -> int:
        return self._Level

    @getLevel.setter
    def getLevel(self, Level: int | str) -> None:
        if isinstance(Level, str):
            Level = Level.upper()
            if Level == "DEBUG":
                self._Level = logging.DEBUG
            elif Level == "INFO":
                self._Level = logging.INFO
            elif Level == "WARNING":
                self._Level = logging.WARNING
            elif Level == "ERROR":
                self._Level = logging.ERROR
            elif Level == "CRITICAL":
                self._Level = logging.CRITICAL
            else:
                self._Level = logging.DEBUG
        elif isinstance(Level, int):
            if Level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
                self._Level = Level
            else:
                self._Level = logging.DEBUG
    
    # Logger configuration
    @property
    def getLogger(self) -> logging.Logger:
        return self._Logger

    @getLogger.setter
    def getLogger(self, Logger: logging.Logger) -> None:
        self._Logger = Logger

    @property
    def getBLoggerStart(self) -> bool:
        return self._BLoggerStart

    @getBLoggerStart.setter
    def getBLoggerStart(self, BLoggerStart: bool) -> None:
        self._BLoggerStart = BLoggerStart

    # Influence on the program excecution
    @property
    def getBLocking(self) -> bool:
        return self._BLocking

    @getBLocking.setter
    def getBLocking(self, BLocking: bool) -> None:
        self._BLocking = BLocking

    # Others data
    @property
    def getCurrentID(self) -> int:
        return self._CurrentID

    @getCurrentID.setter
    def getCurrentID(self, CurrentID: int) -> None:
        self._CurrentID = CurrentID

    @property
    def getTimeOBJ(self):
        return self._TimeOBJ

    @getTimeOBJ.setter
    def getTimeOBJ(self, TimeOBJ) -> None:
        self._TimeOBJ = TimeOBJ

    # Configuration Methods
    def LoggerConfiguration(self, BForceReconfigure: bool = True, BOverWrite: bool = True) -> None:
        """
        Configure the internal logger.

        This method avoids adding duplicate handlers if the MessageManager
        is initialized several times.
        """

        # Set the logger level to save all messages, and let the handlers filter them
        self.getLogger.setLevel(self.getLevel)

        # Disable propagation to avoid duplicate messages in the root logger (received by other subloggers)
        self.getLogger.propagate = False

         # Check if the logger already has handlers to avoid adding duplicates
        if self.getLogger.handlers:
            if BForceReconfigure:
                for Handler in self.getLogger.handlers[:]:
                    Handler.close()
                    self.getLogger.removeHandler(Handler)
            else:
                self.getBLoggerStart = True
                return

        # Create a formatter for the log messages
        Formatter = logging.Formatter(fmt="{asctime} & {levelname:<10} & {name} & {message} & {funcName} & line {lineno}", style="{")

        # Create a rotating file handler to write log messages to a file
        if self.getBRecord:
            if BOverWrite and self.getLogFile.exists():
                self.getLogFile.unlink()

            FileHandler = RotatingFileHandler(filename=self.getLogFile, mode="w", maxBytes=self.getMaxBytes,
                backupCount=self.getBackupCount, encoding="utf-8") # mode="a" if you want to append to the log file instead of overwriting it

            FileHandler.setLevel(self.getLevel)

            FileHandler.setFormatter(Formatter)

            self.getLogger.addHandler(FileHandler)

        if self.getBConsole:
            ConsoleHandler = logging.StreamHandler()

            ConsoleHandler.setLevel(logging.INFO)

            ConsoleHandler.setFormatter(Formatter)

            self.getLogger.addHandler(ConsoleHandler)

        self.getBLoggerStart = True

    # Close the logger and release resources
    def Shutdown(self) -> None:
        logging.shutdown()

    # Message methods

    # Other improoved message methods
    

"""
Message Management objects with GUI

# Improvement to be done:
# -
"""
class MessageGUI(MessageManager):
    def __init__(self):
        super().__init__()
        # Metadata

        # Parameters of the message management

        # Data

        pass

    # Metadata

    # Parameters of the message management

    # Data

    # Basic message functions

    def Start(self):
        """Start the message management GUI."""
        pass

    def Close(self):
        """Close the message management GUI."""
        pass

    # Basic message functions
    # Debug message functions
    def Debug(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.debug(Message, *args, stacklevel=2)

    # Information message functions
    def Info(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.info(Message, *args, stacklevel=2)

    # Warning message functions
    def Warning(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.warning(Message, *args, stacklevel=2)

    # Error message functions
    def Error(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.error(Message, *args, stacklevel=2)

    def Critical(self, Message: str, BLocking: bool = False, *args: object) -> None:
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.critical(Message, *args, stacklevel=2)

    def Exception(self, Message: str, BLocking: bool = False, *args: object) -> None:
        """
        Log an exception with the full traceback.

        Use this method only inside an except block.
        """
        self.getCurrentID += 1
        self.getBLocking = BLocking
        self.getLogger.exception(Message, *args, stacklevel=2)

    # Information message functions
    def show_info(title, message):
        """Show an info message box."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showinfo(title, message)
        root.destroy()

    # Question message functions
    def show_question(title, message):
        """Show a question dialog and return True for Yes or False for No."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        response = messagebox.askyesno(title, message)
        root.destroy()
        return response

    # Warning message functions
    def show_warning(title, message):
        """Show a warning message box."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showwarning(title, message)
        root.destroy()

    # Error message functions
    def show_error(title, message, non_blocking=True):
        """Show an error message box. Defaults to non-blocking."""
        if non_blocking:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            root.after(10, lambda: messagebox.showerror(title, message))
            root.after(100, root.destroy)  # Destroy after short delay
        else:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror(title, message)
            root.destroy()

    # Interactive message functions
    def ask_user_input(title, prompt, expected_type=str):
        """Ask for user input through a simple entry dialog and validate its type."""
        def on_submit():
            nonlocal user_input, valid
            user_input = entry.get()
            try:
                if expected_type == int:
                    user_input = int(user_input)
                elif expected_type == float:
                    user_input = float(user_input)
                elif expected_type == bool:
                    user_input = user_input.lower() in ['true', '1', 'yes']
                elif expected_type == str:
                    user_input = str(user_input)
                valid = True
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", f"Please enter a valid {expected_type.__name__}.")

        user_input = None
        valid = False

        while not valid:
            dialog = tk.Tk()
            dialog.title(title)

            tk.Label(dialog, text=prompt).pack(pady=10)
            entry = tk.Entry(dialog, width=40)
            entry.pack(pady=5)
            entry.focus()

            tk.Button(dialog, text="Submit", command=on_submit).pack(pady=10)

            dialog.mainloop()

        return user_input

    # Cancel/Retry and OK/Cancel message functions
    def show_retry_cancel(title, message):
        """Show a retry/cancel dialog and return True for Retry or False for Cancel."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        response = messagebox.askretrycancel(title, message)
        root.destroy()
        return response

    def show_ok_cancel(title, message):
        """Show an OK/Cancel dialog and return True for OK or False for Cancel."""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        response = messagebox.askokcancel(title, message)
        root.destroy()
        return response



from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import csv
"""
MessageEntry and MessageEntryExt (Extended) Data Class

# Improvement to be done:
# -
"""
@dataclass
class MessageEntry:
    ID: int
    Type: str
    BActivity: bool
    Timestamp: datetime
    Message: str
    FileName: str = None
    Line: int = None

@dataclass
class MessageEntryExt:
    ID: int
    Type: str
    BActivity: str # str "Created", "Updated", "Active", "Inactive", "Deleted" to have a better trace of the message state
    Timestamp: datetime
    Message: str
    FileName: str = None
    Line: int = None

"""
MessagesDataStruct

# Improvement to be done:
# -
"""
class MessagesDataStruct:
    """
    In-memory message database for fast access/update.
    """
    def __init__(self):
        # Data
        self._Messages = {} # Dictionary to store messages by ID, containing the current state of each message
        self._MessageHistory = []  # List to store the history of all messages added, including their previous states

    # Data
    @property
    def getMessages(self):
        return self._Messages

    @getMessages.setter
    def getMessages(self, Messages):
        self._Messages = Messages

    @property
    def getMessageHistory(self):
        return self._MessageHistory

    @getMessageHistory.setter
    def getMessageHistory(self, MessageHistory):
        self._MessageHistory = MessageHistory

    # Data Management Methods
    def Add(self, ID, Type, BActivity, Timestamp, Message, FileName=None, Line=None):
        msg = MessageEntry(
            ID=ID,
            Type=Type,
            BActivity=BActivity,
            Timestamp=Timestamp,
            Message=Message,
            FileName=FileName,
            Line=Line
        )

        self.getMessages[ID] = msg
        self.getMessageHistory.append(ObjectCopy(msg))

        return msg

    def LoadMessages(self, Messages):
        self.clear()
        for msg in Messages:
            self.getMessages[msg.ID] = msg
            self.getMessageHistory.append(ObjectCopy(msg))

    def getID2Message(self, ID):
        return self.getMessages.get(ID)

    def setActivity(self, ID, Active: bool):
        if ID in self.getMessages:
            self.getMessages[ID].BActivity = Active
            self.getMessageHistory.append(ObjectCopy(self.getMessages[ID]))

    def UpdateMessage(self, ID, Text):
        if ID in self.getMessages:
            self.getMessages[ID].Message = Text
            self.getMessageHistory.append(ObjectCopy(self.getMessages[ID]))

    def getAll(self):
        return [self.getMessages[i] for i in range(1, len(self.getMessages) + 1)]

    def getActive(self, BActivity=True):
        if BActivity:
            return [msg for msg in self.getAll() if msg.BActivity]
        else:
            return [msg for msg in self.getAll() if not msg.BActivity]

    def getType(self, Type):
        return [msg for msg in self.getAll() if msg.Type == Type]

    def getLast(self):
        return self.getMessages[len(self.getMessages)] if self.getMessages else None

    def Clear(self):
        self.getMessages.clear()
        self.getMessageHistory.clear()
        self.getOrder.clear()

    def Export2json(self, Filepath):
        Data = [asdict(msg) for msg in self.getMessageHistory]

        if not Data:
            return

        with open(Filepath, "w", encoding="utf-8") as f:
            json.dump(Data, f, indent=4, ensure_ascii=False)

    def Export2csv(self, Filepath):
        Data = [asdict(msg) for msg in self.getMessageHistory]

        if not Data:
            return

        with open(Filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["ID", "Type", "BActivity", "Timestamp", "Message"]
            )
            writer.writeheader()
            writer.writerows(Data)

    def __len__(self):
        return len(self.getMessages)

    def __iter__(self):
        for ID in range(1, len(self.getMessages) + 1):
            yield self.getMessages[ID]

"""
MessageRecorder

# Improvement to be done:
# -
"""
class MessageRecorder:
    """
    Message recorder that appends messages to a JSON file.

    Used for persistent storage of messages, while maintaining efficient access and updates in memory.
    """
    def __init__(self, Filepath: str):
        self.Filepath = Path(Filepath)
        self.Filepath.parent.mkdir(parents=True, exist_ok=True)

    def Append(self, Message: MessageEntry):
        with open(self.Filepath, "a", encoding="utf-8") as f:
            json.dump(asdict(Message), f, ensure_ascii=False)
            f.write("\n")

    def LoadFile(self):
        Messages = []

        if not self.Filepath.exists():
            return Messages

        with open(self.Filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    Data = json.loads(line)
                    Messages.append(MessageEntry(**Data))

        return Messages