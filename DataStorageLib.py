# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Library for data storage and treatment 


# Other Lib
from abc import ABC, abstractmethod

from os import write
from pathlib import Path

from typing import Any, Literal
import shutil

import json
import csv

import numpy as np
import pandas as pd

# Custom Lib
from GUIMessageLib import LogManager

"""
# Improvement to be done:
- Add a master data structure that can save different data types (e.g., dict, list, pandas DataFrame) and handle them in a unified way 
to store each in the appropriate file format (e.g., .dat, .txt, .json, .csv, .sqlite, .toml, .yaml, .pickle, .parquet, .feather, .hdf5).
While being able to read them back into in each file format and convert them back to the master data structure, via a json or yaml file that describes the data structure and the file format to use for each data type.
- Allow to save data after a given amount of records or after a given time interval, to avoid writing to the file too often and to avoid data loss in case of a crash.
by the use of a queue and a dedicated writer thread that writes to the file in a safe way, with a backup file if needed.
"""

"""
Storage: Generic class for data storage and treatment. It is used to store data from different sources and to treat them.

# Improvement to be done:
- For data acquisition, avoid having every scale write directly to the file.

A better architecture is:
Scale thread 1 ─┐
Scale thread 2 ─┼──> Queue ───> Storage writer thread ───> file/database
Scale thread 3 ─┘

Only one thread writes to the file. This avoids file corruption and race conditions.

The writer thread can write:
    - every measurement immediately
    - every 10 measurements
    - every 1 second

For maximum crash safety, write and sync every measurement.

For better performance, write in small batches.
"""
class Storage(ABC):
    def __init__(self, FilePath: str | Path, Name: str | None = None,
        MaxFileSize: int = 10 * 1024 * 1024, BBackupFile: bool = False,
        BackupPath: str | Path | None = None, Logger: LogManager | None = None):

        # Metadata
        self._Name = Name
        self._FileType: str | None = None  # File type (e.g., 'txt', 'csv', 'json', etc.)
               
        # File parameters
        self._FilePath = Path(FilePath)

        self._MaxFileSize = MaxFileSize
        self._FileIndex = 0  # Index for file rotation
        self._LFiles: list[Path] = [self.getFilePath]  # List of rotated files paths

        self._BBackupFile = BBackupFile  # Backup file before overwriting
        self._BackupFilePath = (Path(BackupPath) if BackupPath is not None else self.getFilePath.parent / "Backup") # Backup files path

        # Data parameters


        # Data
        # Add option for data dict, list, queue, panda, etc. For now, use a dict for generic data storage.
        self._Data: dict[Any, Any] = {}

        # Message Handler
        self._Logger = Logger  # LogManager object for handling messages related to the balance

    # Metadata
    @property
    def getName(self) -> str:
        if self._Name is None:
            return self.Filepath.stem
        return self._Name

    @getName.setter
    def getName(self, Name: str) -> None:
        self._Name = Name

    @property
    def getFileType(self) -> str:
        return self._FileType

    @getFileType.setter
    def getFileType(self, FileType: str) -> None:
        self._FileType = FileType

    # File parameters
    @property
    def getFilePath(self) -> Path:
        return self._FilePath

    @getFilePath.setter
    def getFilePath(self, FilePath: str | Path) -> None:
        self._FilePath = Path(FilePath)

    @property
    def getMaxFileSize(self) -> int:
        return self._MaxFileSize

    @getMaxFileSize.setter
    def getMaxFileSize(self, MaxFileSize: int) -> None:
        self._MaxFileSize = MaxFileSize

    @property
    def getFileIndex(self) -> int:
        return self._FileIndex

    @getFileIndex.setter
    def getFileIndex(self, FileIndex: int) -> None:
        self._FileIndex = FileIndex

    @property
    def getLFiles(self) -> list[str]:
        return self._LFiles

    @getLFiles.setter
    def getLFiles(self, LFiles: list[str] | str) -> None:
        if isinstance(LFiles, str):
            self._LFiles.append(LFiles)
        else:
            self._LFiles = LFiles

    @property
    def getBBackupFile(self) -> bool:
        return self._BBackupFile

    @getBBackupFile.setter
    def getBBackupFile(self, BBackupFile: bool) -> None:
        self._BBackupFile = BBackupFile

    @property
    def getBackupFilePath(self) -> Path:
        return self._BackupFilePath

    @getBackupFilePath.setter
    def getBackupFilePath(self, BackupFilePath: str | Path) -> None:
        self._BackupFilePath = (Path(BackupFilePath) if BackupFilePath is not None else self.getFilePath.parent / "Backup")

    # Data parameters

    # Data
    @property
    def getData(self) -> dict[Any, Any]:
        return self._Data

    @getData.setter
    def getData(self, Data: dict[Any, Any]) -> None:
        self._Data = Data

    # Methods for generic data storage and retrieval
    def DataSet(self, Key: Any, Value: Any) -> None:
        """Store or update a value."""
        self.getData[Key] = Value

    def DataAppend(self, Key: Any, Value: Any) -> None:
        """Append a value to a list stored under the given key."""
        if Key not in self.getData:
            self.getData[Key] = []

        if not isinstance(self.getData[Key], list):
            raise TypeError(f"Data under key '{Key}' is not a list.")

        if isinstance(Value, list):
            self.getData[Key].extend(Value)
        else:
            self.getData[Key].append(Value)

    def DataGet(self, Key: Any, Default: Any = None) -> Any:
        """Read a value from memory."""
        return self.getData.get(Key, Default)

    def DataDelete(self, Key: Any) -> None:
        """Delete a value."""
        if Key in self.getData:
            del self.getData[Key]

    def DataClear(self) -> None:
        """Clear all data."""
        self.getData.clear()

    def DataConvert(self, Value: Any, Type: str) -> Any:
        if Type == "int":
            return int(Value)
        elif Type == "float":
            return float(Value)
        elif Type == "bool":
            return str(Value).strip().lower() in ("true", "1", "yes")  # Value.lower() in ("true", "1", "yes")
        elif Type == "str":
            return str(Value)
        elif Type == "none":
            return None
        else:
            return Value

    # Test and debug
    @property
    def getLogger(self) -> LogManager | None:
        return self._Logger

    @getLogger.setter
    def getLogger(self, Logger: LogManager | None) -> None:
        if not isinstance(Logger, LogManager):
            raise TypeError("Error: Logger must be an instance of LogManager.")

        if Logger.getBLoggerStart:
            self._Logger = Logger
        else:
            raise ValueError("Error: Logger must be started before assignment.")

    @property
    def getBLogger(self) -> bool:
        return self._Logger is not None

    # File operations
    @abstractmethod
    def Write(self) -> None:
        """
        Write data to the file, overwriting existing content.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support Write().")

    @abstractmethod
    def Append(self, Data: Any) -> None:
        """
        Append data to the file and Storage object, preserving existing content.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support Append().")

    @abstractmethod
    def Read(self) -> Any:
        """
        Read data from the file, store it inside the Storage object and return it in the appropriate format. 
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support Read().")

    def Backup(self, Suffix : str | None = "Temp") -> None:
        """
        Generate a backup of the file before overwriting it.
        The backup file will be named with file name and a temporary suffix (TEMP)
        """
        if self.getBBackupFile:

            self.getBackupFilePath.mkdir(parents=True, exist_ok=True)

            BackupFilePath = self.getBackupFilePath / f"{self.getFilePath.stem}_{Suffix}{self.getFilePath.suffix}"

            shutil.copy2(self.getFilePath, BackupFilePath)

            return BackupFilePath

        else:  # Do not need to create a backup file
            return None

    def Rotating(self) -> bool:
        """
        Manage file rotation based on the maximum file size. If the current file exceeds the maximum size, 
        it will be renamed with a numeric suffix, and a new file need to be created, the old one will be kept and not overwritten.

        Returns:
            bool: True if the file was rotated and new file need to be created, False otherwise.
        """
        if self.getFilePath.exists() and self.getFilePath.stat().st_size > self.getMaxFileSize: # File exists and exceeds the maximum size

            # Rotate the file
            NewFilePath = self.getFilePath.with_name(f"{self.getFilePath.stem}_{self.getFileIndex}{self.getFilePath.suffix}")

            self.getLFiles.append(NewFilePath)

            self.getFilePath = NewFilePath

            self.getFileIndex += 1

            return True

        return False
        
    def BPathExists(self) -> bool:
        """
        Verify if the file exists. Returns True if the file exists, otherwise False.
        """
        return Path(self.getFilePath).exists()

    def DeleteCurrentFile(self) -> None:
        """
        Delete the current file associated with this storage object. If the file does not exist, nothing happens.
        """
        if self.getFilePath.exists():
            FileDelete(self.getFilePath)

    def DeleteBackupFiles(self) -> None:
        """
        Delete the backup file associated with this storage object. If the backup file does not exist, nothing happens.
        """
        if self.getBBackupFile:
            if self.getBackupFilePath.exists() and self.getBackupFilePath.is_dir():
                DirDelete(self.getBackupFilePath)
            else:
                FileDelete(self.getBackupFilePath)

    def DeleteFiles(self) -> None:
        """
        Delete all files associated with this storage object. Including the backup file if it exists. 
        The backup file path is kept and not deleted.
        """
        self.DeleteBackupFiles()

        for FilePath in self.getLFiles:
            if FilePath.exists():
                FileDelete(FilePath)

        self.getLFiles.clear()


def FileDelete(FilePath: str | Path) -> None:
        """
        Delete a specific file.
        """
        if FilePath.exists():
            if FilePath.is_file() or FilePath.is_symlink():
                FilePath.unlink()
            else:
                raise IsADirectoryError(f"{FilePath} is a directory, not a file.")

def DirDelete(DirPath: str | Path) -> None:
        """
        Delete a specific directory and all its contents.
        """
        if DirPath.exists():
            if DirPath.is_dir():
                shutil.rmtree(DirPath)
            else:
                raise NotADirectoryError(f"{DirPath} is not a directory.")
"""
StorageDat

Human readable:
    No.

Supports:
    Fixed-size structured binary records, usually numbers, booleans,
    timestamps, IDs, and other simple typed fields.

Methods:
    - Read binary records from a .dat file.
    - Write binary records to a .dat file.
    - Append binary records efficiently.

Best use:
    Fast and compact storage of repeated measurements.

Limitations:
    - The file structure must be known in advance.
    - Variable-length text is more difficult to store.
    - Not directly readable without a dedicated parser.

Improvements to be done:
    - Add a file header with format version and metadata.
    - Add safe append with flush() and os.fsync().
    - Detect and ignore incomplete final records after a crash.
"""

"""
StorageTxt

Human readable:
    Yes.

Supports:
    Plain text data, usually strings. Other types such as int, float,
    bool, list, dict, and None must be manually converted to and from text.

Methods:
    - Read text files.
    - Write text files.
    - Append text lines.

Best use:
    Notes, simple logs, reports, and simple text-based exports.

Limitations:
    - No automatic type preservation.
    - Not ideal for structured data unless a custom format is defined.

Improvements to be done:
    - Add line-by-line append.
    - Add encoding handling.
    - Add optional safe write using a temporary file.
"""



"""
StorageJSON

Human readable:
    Yes.

Supports:
    str, int, float, bool, list, dict, and None.

Methods:
    - Read JSON files.
    - Write JSON files.
    - Update dictionary-like JSON data.

Best use:
    Configuration files, metadata, settings, and small structured datasets.

Limitations:
    - Not ideal for continuous append.
    - The whole file usually has to be rewritten after modification.
    - Does not natively support datetime, Path, Decimal, NumPy arrays,
      or custom Python objects.

Improvements to be done:
    - Add support for safe atomic write.
    - Add optional custom encoder/decoder for datetime and Path.
    - Add validation of expected keys and data types.
"""
import json
from typing import Any


class StorageJSON(Storage):
    def __init__(self, filepath: str | Path, name: str | None = None):
        super().__init__(filepath, name)
        self.file_type = "json"

    def Write(self, data: dict[str, Any]) -> None:
        if self.backup_enabled:
            self.backup()

        with self.filepath.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def read(self) -> dict[str, Any]:
        if not self.filepath.exists():
            return {}

        with self.filepath.open("r", encoding="utf-8") as file:
            return json.load(file)

    def append(self, data: dict[str, Any]) -> None:
        current_data = self.read()
        current_data.update(data)
        self.write(current_data)

"""
StorageJSONLines

Human readable:
    Yes.

Supports:
    str, int, float, bool, list, dict, and None.

Methods:
    - Append one JSON object per line.
    - Read JSON records line by line.
    - Write or export JSONL files.

Best use:
    Continuous measurement logs, event logs, and append-oriented structured data.

Limitations:
    - The file is not one single valid JSON object.
    - Each line must be parsed independently.
    - A crash may corrupt the last line, which should be detected and ignored.

Improvements to be done:
    - Add safe append with flush() and os.fsync().
    - Add recovery by skipping incomplete or invalid final lines.
    - Add optional compression for old files.
"""

"""
StorageCSV

Human readable:
    Yes.

Supports:
    Flat/tabular data only.

Methods:
    - Read CSV files.
    - Write CSV files.
    - Append rows to CSV files.

Best use:
    Measurement tables, simple exports, spreadsheet-compatible data.

Limitations:
    - No nested structures.
    - Type information is weak: values are often read back as strings.
    - Changing columns after file creation can be inconvenient.

Improvements to be done:
    - Add safe append with flush() and os.fsync().
    - Add automatic header creation.
    - Add type conversion when reading.
    - Add validation of required columns.
"""

class StorageCSV(Storage):
    def __init__(self, FilePath: str | Path, FieldNames: list[str] | None = None, FieldTypes: list[str] | None = None,
                 Name: str | None = None, MaxFileSize: int = 10 * 1024 * 1024, 
                 BBackupFile: bool = False, BackupPath: str | Path | None = None, Logger: LogManager | None = None):
        super().__init__(FilePath=FilePath, Name=Name, MaxFileSize=MaxFileSize, 
                         BBackupFile=BBackupFile, BackupPath=BackupPath, Logger=Logger)

        # Metadata
        
        # File parameters

        # Data parameters

        # Data
        self._FieldNames = [""]
        self._FieldTypes = [""]

        #
        self.getFieldNames = FieldNames
        self.getFieldTypes = FieldTypes

        if not self.BPathExists():
            with self.getFilePath.open("w", newline="", encoding="utf-8") as File:
                Writer = csv.writer(File, delimiter='&')

    # Metadata
        
    # File parameters

    # Data parameters

    # Data
    @property
    def getFieldNames(self) -> list[str]:
        return self._FieldNames

    @getFieldNames.setter
    def getFieldNames(self, FieldNames: list[str] | None) -> None:
        if FieldNames is None:
            self._FieldNames = [""]
        else:
            self._FieldNames = FieldNames

    @property
    def getFieldTypes(self) -> list[str]:
        return self._FieldTypes

    @getFieldTypes.setter
    def getFieldTypes(self, FieldTypes: list[str] | None) -> None:
        if FieldTypes is not None:
            if len(FieldTypes) < len(self.getFieldNames):
                self._FieldTypes = FieldTypes + ([""] * (len(self.getFieldNames) - len(FieldTypes)))
            else:
                self._FieldTypes = FieldTypes
        else:
            self._FieldTypes = [""]

    # File operations
    def Write(self) -> None:
        """
        Write data to the file, overwriting existing content and generating a backup if enabled.
        """
        with self.getFilePath.open("w", newline="", encoding="utf-8") as File:
            Writer = csv.writer(File, delimiter='&')

            Writer.writerow(self.getFieldNames)  # First header line: field names
            Writer.writerow(self.getFieldTypes)  # Second header line: field types

        self.Rotating()

        with self.getFilePath.open("a", newline="", encoding="utf-8") as File:
            Writer = csv.writer(File, delimiter='&')

            LData = []

            for Key, Value in self.getData.items():
                LData.append([Key] + Value)

            Writer.writerows(LData)

        if self.getBBackupFile:
            self.Backup()

    def Append(self, Data: dict) -> None:
        """
        Append data to the file and Storage object, preserving existing content.
        """
        if not self.BPathExists():
            with self.getFilePath.open("w", newline="", encoding="utf-8") as File:
                Writer = csv.writer(File, delimiter='&')

                Writer.writerow(self.getFieldNames)  # First header line: field names
                Writer.writerow(self.getFieldTypes)  # Second header line: field types

        self.getData.update(Data)

        if not (self.BPathExists() and self.getFilePath.stat().st_size > 0):
            self.Write()
            return
        
        self.Rotating()

        with self.getFilePath.open("a", newline="", encoding="utf-8") as File:
            Writer = csv.writer(File, delimiter='&')

            LData = [[Key] + Value for Key, Value in Data.items()]

            Writer.writerows(LData)

        if self.getBBackupFile:
            self.Backup()

    def Read(self) -> Any:
        """
        Read data from the file, store it inside the Storage object and return it in the appropriate format. 
        """
        if not self.BPathExists():
            print(f"Error: File {self.getFilePath} does not exist.")
            return None

        with self.getFilePath.open("r", newline="", encoding="utf-8") as File:
            Reader = csv.reader(File, delimiter='&')

            self.getFieldNames = next(Reader, [])  # First header line: field names
            self.getFieldTypes = next(Reader, [])  # Second header line: field types

            #self.DataAppend(Key=self.getFieldNames[0], Value=self.getFieldNames[1:])

            #for FieldName, FieldType in zip(self.getFieldNames, self.getFieldTypes):
            #    self.DataAppend(Key=FieldName, Value=FieldType)

            for Row in Reader:
                if not Row:
                    continue

                FieldTypes = self.getFieldTypes + ([""] * (len(Row) - len(self.getFieldTypes)))

                ConvertedRow = [self.DataConvert(Value=Data, Type=Type) for Data, Type in zip(Row, FieldTypes)]

                self.DataAppend(Key=ConvertedRow[0], Value=ConvertedRow[1:])

            return self.getData
        
"""
StorageSQLite

Human readable:
    Not directly human readable.

Supports:
    Structured relational data using SQL types such as INTEGER, REAL,
    TEXT, BLOB, and NULL. More complex Python objects must be serialized
    before storage.

Methods:
    - Insert, read, update, and delete records.
    - Execute SQL queries.
    - Use transactions.
    - Use indexes for fast search.
    - Use WAL mode for robust append-heavy workflows.

Best use:
    Robust long-term storage of measurements, metadata, calibration data,
    experiment information, and logs.

Limitations:
    - Requires basic SQL knowledge.
    - Not directly editable like CSV or JSON.
    - Schema design is needed.

Improvements to be done:
    - Enable WAL mode.
    - Add transactions.
    - Add indexes on timestamp and balance ID.
    - Add one dedicated writer thread for multi-scale acquisition.
"""

"""
StorageTOML

Human readable:
    Yes, very readable.

Supports:
    str, int, float, bool, list, dict-like tables, dates, and None-like
    values depending on the TOML library used.

Methods:
    - Read TOML configuration files.
    - Write TOML configuration files, if a writing library is available.

Best use:
    Configuration files, project settings, scale setup, logging settings.

Limitations:
    - Python's built-in tomllib can read TOML but cannot write it.
    - Not intended for continuous measurement logging.
    - Less flexible than JSON for arbitrary nested data.

Improvements to be done:
    - Add support for tomli-w or tomlkit for writing.
    - Add validation of configuration fields.
    - Add default configuration generation.
"""

"""
StorageYAML

Human readable:
    Yes, very readable.

Supports:
    str, int, float, bool, list, dict, None, and complex nested structures.

Methods:
    - Read YAML files.
    - Write YAML files.

Best use:
    Configuration files with nested structures.

Limitations:
    - Requires an external package such as PyYAML.
    - Indentation errors can break the file.
    - Unsafe loading can be dangerous; safe_load should be used.
    - Not ideal for continuous measurement logging.

Improvements to be done:
    - Use yaml.safe_load() and yaml.safe_dump().
    - Add schema validation.
    - Add clear error messages for invalid YAML.
"""

"""
StoragePickle

Human readable:
    No.

Supports:
    Most Python objects, including custom classes and complex structures.

Methods:
    - Serialize Python objects to binary files.
    - Deserialize Python objects from binary files.

Best use:
    Temporary Python-only storage, caching, and internal program state.

Limitations:
    - Not safe to load from untrusted sources.
    - Python-specific.
    - Not recommended for long-term storage.
    - Not human readable.
    - Can break if class definitions change.

Improvements to be done:
    - Add a clear warning before loading pickle files.
    - Add versioning for stored objects.
    - Avoid using it for critical measurement archives.
"""

"""
StorageParquet

Human readable:
    No.

Supports:
    Large tabular datasets with typed columns.

Methods:
    - Read Parquet files.
    - Write Parquet files.
    - Efficiently store and load column-oriented data.

Best use:
    Large datasets, pandas DataFrames, data analysis, compressed archives.

Limitations:
    - Requires external libraries such as pandas, pyarrow, or fastparquet.
    - Not ideal for one-row-at-a-time append.
    - Better for batch export than live acquisition.

Improvements to be done:
    - Add batch writing.
    - Add compression options.
    - Add conversion from SQLite or CSV to Parquet for analysis.
"""

"""
StorageFeather

Human readable:
    No.

Supports:
    Tabular datasets with typed columns.

Methods:
    - Read Feather files.
    - Write Feather files.
    - Fast exchange of DataFrame-like data.

Best use:
    Fast local loading and saving of pandas DataFrames.

Limitations:
    - Requires pyarrow.
    - Not ideal for continuous append.
    - Less suitable than SQLite or JSONL for crash-safe acquisition.

Improvements to be done:
    - Add batch export from measurement storage.
    - Add compatibility with pandas DataFrames.
"""

"""
StorageHDF5

Human readable:
    No.

Supports:
    Large datasets, hierarchical groups, arrays, metadata, and scientific data.

Methods:
    - Read HDF5 files.
    - Write HDF5 files.
    - Store hierarchical datasets.

Best use:
    Scientific datasets, large arrays, experiment archives, and hierarchical data.

Limitations:
    - Requires external libraries such as h5py or pandas.
    - More complex than CSV, JSONL, or SQLite.
    - Concurrent writing must be handled carefully.
    - Not ideal as a first storage backend unless large scientific arrays are needed.

Improvements to be done:
    - Add clear group/dataset structure.
    - Add metadata storage.
    - Add safe closing and flushing.
    - Add batch writing instead of one-value-at-a-time writing.
"""




"""
DataLog

# Improvement to be done:

"""
class DataLog:
    def __init__(self):
        # File
        self.FileName = None
        self.ApprovedFiles = []

        # Data
        self.Data = None
        self.DataMatrix = None

        # Data Analysis and Visualization
        self.AbsCol = None
        self.OrdCol = None
        self.TimeCol = None
        self.SelectCol = None

        self.AbsVal = None
        self.OrdVal = None
        self.TimeVal = None

        self.PLTIndex = None
        self.PLTDataMatrix = None

        self.TimeStepArray = None

        # Register for functions
        self.FuncInput = None # Data let to be used by other functions
        self.FuncTempData = None
        self.FuncOutput = None


    # File
    @property
    def getFileName(self):
        return self.FileName

    @getFileName.setter
    def getFileName(self, value):
        self.FileName = value

    @property
    def getApprovedFiles(self):
        return self.ApprovedFiles

    @property
    def BoolApprovedFiles(self):
        """Returns True if the filename is in the approved list, otherwise False."""
        if self.FileName is not None:
            return any(self.getFileName.endswith(ext) for ext in self.getApprovedFiles)
        return False
    

    # Data
    @property
    def getData(self):
        return self.Data

    @getData.setter
    def getData(self, value):
        self.Data = value

    @property
    def getDataMatrix(self):
        return self.DataMatrix

    @getDataMatrix.setter
    def getDataMatrix(self, Matrix):
        self.DataMatrix = Matrix

    @property
    def getNRow(self):
        """
        Returns the number of rows in the data matrix.
        """
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None
        print("Number of rows: [ 0 ;", self.getDataMatrix.shape[0], "]")

        return self.getDataMatrix.shape[0]

    @property
    def getNRowSimpli(self):
        """
        Returns the number of rows in the data matrix. Simplified version, without print
        """
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None

        return self.getDataMatrix.shape[0]

    @property
    def getNCol(self):
        """
        Returns the number of columns in the data matrix.
        """
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None
        print("Number of columns: [ 0 ;", self.getDataMatrix.shape[1], "]")

        return self.getDataMatrix.shape[1]

    @property
    def getNColSimpli(self):
        """
        Returns the number of columns in the data matrix. Simplified version, without print
        """
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None

        return self.getDataMatrix.shape[1]

    @property
    def getNStep(self):
        """
        Returns the number of time steps in the data matrix.
        """
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None

        if self.getTimeCol is None:
            print("Error: No time column selected.")
            return None

        # Extract the time steps
        if self.getTimeStepArray is None:
            TimeStepArray = self.SetTimeStepArray
        else:
            TimeStepArray = self.getTimeStepArray

        # Count the number of time steps
        NStep = len(TimeStepArray)

        print("Number of time steps: [ 0 ;", NStep, "]")
        return NStep

    @property
    def getNStepSimpli(self):
        """
        Returns the number of time steps in the data matrix. Simplified version, without print
        """
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None

        if self.getTimeCol is None:
            print("Error: No time column selected.")
            return None

        # Extract the time steps
        if self.getTimeStepArray is None:
            TimeStepArray = self.SetTimeStepArray
        else:
            TimeStepArray = self.getTimeStepArray

        # Count the number of time steps
        NStep = len(TimeStepArray)

        return NStep

    def getUniqueSteps(self, IntCol):
        """
        Returns the unique time steps in the data matrix.

        Args:
            IntCol (int): Column index for time steps.

        Returns:
            UniqueValArray (array): Array of unique time steps.
        """
        # Verify that the data matrix is not empty
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return None

        # Verify that the column index is valid
        if IntCol < 0 or IntCol >= self.getNColSimpli:
            print("Error: Invalid column index.")
            return None
        
        # Extract the array of values from the specified column
        ValArray = self.getDataMatrix[:, IntCol]
        # Extract the unique values
        UniqueValArray = np.unique(ValArray)
        SortUniqueValArray = np.sort(UniqueValArray)
        return SortUniqueValArray, len(SortUniqueValArray)

    @property
    def getUniqueTimeSteps(self):
        """
        Returns the unique time steps in the data matrix.
        """
        if self.getTimeCol is None:
            print("Error: No time column selected.")
            return None
        return self.getUniqueSteps(self.getTimeCol)


    # Data Analysis and Visualization
    @property
    def getAbsCol(self):
        return self.AbsCol

    @getAbsCol.setter
    def getAbsCol(self, value):
        self.AbsCol = value

    @property
    def getOrdCol(self):
        return self.OrdCol

    @getOrdCol.setter
    def getOrdCol(self, value):
        self.OrdCol = value

    @property
    def getTimeCol(self):
        return self.TimeCol

    @getTimeCol.setter
    def getTimeCol(self, value):
        self.TimeCol = value

    @property
    def getSelectCol(self):
        return self.SelectCol

    @getSelectCol.setter
    def getSelectCol(self, value):
        self.SelectCol = value

    @property
    def getAbsVal(self):
        return self.AbsVal

    @getAbsVal.setter
    def getAbsVal(self, Array):
        self.AbsVal = Array

    @property
    def getOrdVal(self):
        return self.OrdVal

    @getOrdVal.setter
    def getOrdVal(self, Array):
        self.OrdVal = Array

    @property
    def getTimeVal(self):
        return self.TimeVal

    @getTimeVal.setter
    def getTimeVal(self, Array):
        self.TimeVal = Array

    @property
    def getPLTIndex(self):
        return self.PLTIndex

    @getPLTIndex.setter
    def getPLTIndex(self, Array):
        self.PLTIndex = Array

    @property
    def getPLTDataMatrix(self):
        return self.PLTDataMatrix

    @getPLTDataMatrix.setter
    def getPLTDataMatrix(self, Matrix):
        self.PLTDataMatrix = Matrix

    @property
    def ResetPLTIndex(self):
        """ Resets the index selection array."""
        self.PLTIndex = np.arange(self.getNRowSimpli)
        self.getPLTDataMatrix = self.getDataMatrix

    @property
    def getTimeStepArray(self):
        return self.TimeStepArray

    @getTimeStepArray.setter
    def getTimeStepArray(self, Array):
        self.TimeStepArray = Array

    @property
    def SetTimeStepArray(self):
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return False

        if self.getTimeCol is None:
            print("Error: No time column selected.")
            return False

        # Extract the time values
        TimeVal = self.getDataMatrix[:, self.getTimeCol]

        # Extract the unique time steps
        self.getTimeStepArray = np.unique(TimeVal)
        return self.getTimeStepArray


    # Register for functions
    @property
    def ResetFuncRegister(self):
        """
        Resets the function register.
        """
        self.FuncInput = None
        self.FuncTempData = None
        self.FuncOutput = None

    @property
    def getFuncInput(self):
        return self.FuncInput

    @getFuncInput.setter
    def getFuncInput(self, Data):
        self.FuncInput = Data

    @property
    def getFuncTempData(self):
        return self.FuncTempData

    @getFuncTempData.setter
    def getFuncTempData(self, Data):
        self.FuncTempData = Data

    @property
    def getFuncOutput(self):
        return self.FuncOutput

    @getFuncOutput.setter
    def getFuncOutput(self, Data):
        self.FuncOutput = Data


    """
    # Methods
    """
    # File loading
    def LoadFile(self, BLoadMatrix=False):
        """
        Reads the file and extracts numerical data, keeping row structure intact.
        """
        if not self.BoolApprovedFiles:
            print("Error: File format not approved.")
            return None

        # Handling CSV and TXT files
        if self.FileName.endswith(('.csv', '.txt')):
            try:
                self.getData = pd.read_csv(self.FileName, header=None, sep=r'\s+', engine="python").values

                if BLoadMatrix:
                    self.LoadDataMatrix()
                return self.getData

            except Exception as e:
                print(f"Error reading file {self.FileName}: {e}")
                return None

        # Handling IPE and IPN files
        elif self.FileName.endswith(('ipe', 'IPE', 'ipn', 'IPN')):
            try:
                with open(self.FileName, 'r') as file:
                    lines = file.readlines()

                # Detect where numeric data starts and store rows properly
                DataRows = []
                for line in lines:
                    try:
                        DataRows.append([float(Num) for Num in line.split()])
                    except ValueError:
                        continue  # Skip non-numeric lines

                self.getData = DataRows

                if BLoadMatrix:
                    self.LoadDataMatrix()
                return self.getData

            except Exception as e:
                print(f"Error reading file {self.FileName}: {e}")
                return None

        # Handling f71 and F71 files
        elif self.FileName.endswith(('.f71', '.F71')):
            try:
                with open(self.FileName, 'r') as file:
                    lines = file.readlines()

                DataRows, CurrentGroup = [], []
                Capturing = False # Flag to indicate if we are capturing data (Initially not capturing data)
                for line in lines:
                    line = line.strip() # Remove leading/trailing whitespace
                    if not line: 
                        continue  # Skip empty lines
                    try:
                        # Attempt to parse floats from line
                        Values = [float(Val) for Val in line.split()]
                        if not Capturing: # If have finished loading data then create a new current group
                            CurrentGroup = []
                            Capturing = True
                        CurrentGroup.extend(Values) # Add the values to the current group
                    except ValueError:
                        # Line is not numeric
                        if Capturing: # If we are capturing data and encouter a new group
                            if CurrentGroup:
                                DataRows.append(CurrentGroup)
                                CurrentGroup = []
                            Capturing = False
                        # If there are data after the non-numeric line, we need to add them to the current group. If not, we can skip the line.
                        # Try to extract any numeric values from the non-numeric line
                        Values = []
                        for val in line.split():
                            try:
                                Values.append(float(val))
                            except ValueError:
                                continue
                        if Values:
                            if not Capturing: # If have finished loading data then create a new current group
                                CurrentGroup = []
                                Capturing = True
                            CurrentGroup.extend(Values)
                # Append last group if still capturing
                if CurrentGroup:
                    DataRows.append(CurrentGroup)          

                self.getData = DataRows

                if BLoadMatrix:
                    self.LoadDataMatrix()
                return self.getData

            except Exception as e:
                print(f"Error reading Fortran file {self.FileName}: {e}")
                return None

  
    def LoadDataMatrix(self):
        """
        Returns the extracted data as a NumPy matrix.
        """
        if self.getData is None:
            print("Error: No data to convert.")
            return False

        self.getDataMatrix = np.array(self.getData)
        return self.getDataMatrix

    # Data Analysis and Visualization
    def SelectIndex(self, Col=None, Val=None, Tol=0.001, AbsTol=None, ValMin=None, ValMax=None, BClosest=False):
        """
        Selects rows based on the values in a column and updates the index selection array.

        Args:
            Col (int): Column index to select by.
            Val (float): Value to select.
            Tol (float): Tolerance for selection.
            AbsTol (float): Absolute tolerance for selection.
            ValMin (float): Minimum value for selection.
            ValMax (float): Maximum value for selection.
            BClosest (bool): If True, selects the closest value to val value instead of exact match.
        
        Improvements:
        - Add the possibility to extract the values directly from the pltDataMatrix
        """
        # Verify that the data matrix is not empty
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return False

        # Select the column to select by
        if Col is None:
            if self.getSelectCol is None:
                print("Error: No column selected.")
                return False
            Col = self.getSelectCol

        # Extract the values of the selected column inside the data matrix
        ArrayExtractedVal = self.getDataMatrix[:, Col]

        # Select rows based on the values in the column
        if Val is not None and BClosest is False:
            # Get the accepted tolerance
            if AbsTol is None:
                AbsTol = np.abs(Tol*Val)

            # Get the indexes of the values that are within the tolerance to the given value
            NewPLTIndex = np.where(np.abs(ArrayExtractedVal - Val) <= AbsTol)[0]

        elif ValMin is not None and ValMax is not None:
            # Select the values in the range [ValMin, ValMax]
            NewPLTIndex = np.where((ArrayExtractedVal >= ValMin) & (ArrayExtractedVal <= ValMax))[0]

        elif BClosest:
            # Find the index of the closest value to the given value
            IndexClosestVal = np.argmin(np.abs(ArrayExtractedVal - Val))

            # Get the first closest value to the given value and will be used to select the values within the tolerance
            ValClosest = ArrayExtractedVal[IndexClosestVal]

            # Get the accepted tolerance
            if AbsTol is None:
                AbsTol = np.abs(Tol*ValClosest)

            # Get the indexes of the values that are within the tolerance to the closest value (Close enough to the given value)
            NewPLTIndex = np.where(np.abs(ArrayExtractedVal - ValClosest) <= AbsTol)[0]

        else:
            print("Error: No value or range selected.")
            return False

        # Update the index selection array
        if self.getPLTIndex is not None and NewPLTIndex is not None:
            self.getPLTIndex = np.intersect1d(self.getPLTIndex, NewPLTIndex)
        else:
            self.getPLTIndex = NewPLTIndex

        # Verifies that the selection is not empty
        if len(self.getPLTIndex) == 0:
            print("Warning: No data selected.")

        # Update the PLTDataMatrix
        if self.getPLTDataMatrix is not None:
            self.getPLTDataMatrix = self.getDataMatrix[self.getPLTIndex, :]
        else:
            self.getPLTDataMatrix = self.getDataMatrix[self.getPLTIndex, :]

    def SelectTime(self, Val=None, Tol=0, AbsTol=None, ValMin=None, ValMax=None, BClosest=False):
        self.SelectIndex(Col=self.getTimeCol,
                         Val=Val, Tol=Tol, AbsTol=AbsTol,
                         ValMin=ValMin, ValMax=ValMax, BClosest=BClosest)

    def SelectAbs(self, Val=None, Tol=0, AbsTol=None, ValMin=None, ValMax=None, BClosest=False):
        self.SelectIndex(Col=self.getAbsCol,
                         Val=Val, Tol=Tol, AbsTol=AbsTol,
                         ValMin=ValMin, ValMax=ValMax, BClosest=BClosest)

    def SelectOrd(self, Val=None, Tol=0, AbsTol=None, ValMin=None, ValMax=None, BClosest=False):
        self.SelectIndex(Col=self.getOrdCol,
                         Val=Val, Tol=Tol, AbsTol=AbsTol,
                         ValMin=ValMin, ValMax=ValMax, BClosest=BClosest)

    def SelectIndexNoDuplicate(self, Col=None, Tol=0.001, AbsTol=None, ValPolicy=0):
        """
        From the selected index, select the unique values in the given column.

        Args:
            Col (int): Column index to select by.
            Tol (float): Tolerance for selection.
            AbsTol (float): Absolute tolerance for selection.
            ValPolicy (int): Policy for selecting the value to keep in case of duplicates. (-1: last, 0: first, x: x+1th value)
        
        Improvements:
        - Add the possibility to extract the values directly from the pltDataMatrix
        """
        # Verify that the data matrix is not empty
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return False

        # Select the column to select by
        if Col is None:
            if self.getSelectCol is None:
                print("Error: No column selected.")
                return False
            Col = self.getSelectCol

        # Extract the values of the selected column inside the data matrix
        ArrayExtractedVal = self.getDataMatrix[:, Col]

        # In case AbsTol is None, the tolerance is set based on the relative tolerance
        if AbsTol is None:
            BRelTol = True
        else:
            BRelTol = False

        # Sort the values and keep the indices
        SortedIndices = np.argsort(ArrayExtractedVal)
        SortedArrayExtractedVal = ArrayExtractedVal[SortedIndices]

        # Append a dummy value to trigger final group processing
        if BRelTol:
            DummyVal = SortedArrayExtractedVal[-1] + 10 * np.abs(Tol * (SortedArrayExtractedVal[-1] + 1))
        else:
            DummyVal = SortedArrayExtractedVal[-1] + 10 * AbsTol

        SortedArrayExtractedVal = np.append(SortedArrayExtractedVal, DummyVal)
        SortedIndices = np.append(SortedIndices, -1) # dummy index to match length

        NewPLTIndex = []  # Index kept for the unique values
        TempIndexList = []  # List to keep temporarily the indices of the duplicates
        Counter = 0  # Counter for duplicates

        for i in range(len(SortedArrayExtractedVal) - 1):
            CurrentVal = SortedArrayExtractedVal[i]
            NextVal = SortedArrayExtractedVal[i + 1]

            # Get the accepted absolute tolerance if not given. Based on the relative tolerance
            if BRelTol:
                AbsTol = np.abs(Tol * CurrentVal)

            # Check if the difference between the current and previous value is greater than the absolute tolerance
            if np.abs(NextVal - CurrentVal) > AbsTol:
                # The value is unique
                if Counter == 0:
                    # If the value is unique, keep it
                    NewPLTIndex.append(SortedIndices[i])
                else:
                    # If there are duplicates values

                    # Add the last index of the duplicates in the temporary list
                    TempIndexList.append(SortedIndices[i])

                    # Choose the index to be kept
                    KeptSubIndex = ValPolicy

                    if KeptSubIndex >= len(TempIndexList):
                        # If the number of duplicates is less than the value to keep, take the last one
                        KeptSubIndex = -1
                    elif KeptSubIndex < -1:
                        # If the value to keep is negative, take the last one
                        KeptSubIndex = -1

                    if TempIndexList[KeptSubIndex] != -1:
                        NewPLTIndex.append(TempIndexList[KeptSubIndex])

                # Reset the list of temporary indexess
                TempIndexList = []
                # Reset the counter
                Counter = 0

            else:
                # The value is not unique and needs to be kept to check after wich one to choose
                TempIndexList.append(SortedIndices[i])  # Keep the index of the duplicate value
                # Update the counter
                Counter += 1

        # Sort the index of the kept values by resorting the original array
        NewPLTIndex = np.array(NewPLTIndex)
        NewPLTIndex = np.sort(NewPLTIndex)

        # Update the index selection array
        if self.getPLTIndex is not None and NewPLTIndex is not None:
            self.getPLTIndex = np.intersect1d(self.getPLTIndex, NewPLTIndex)
        else:
            self.getPLTIndex = NewPLTIndex

        # Verifies that the selection is not empty
        if len(self.getPLTIndex) == 0:
            print("Warning: No data selected.")

        # Update the PLTDataMatrix
        if self.getPLTDataMatrix is not None:
            self.getPLTDataMatrix = self.getDataMatrix[self.getPLTIndex, :]
        else:
            self.getPLTDataMatrix = self.getDataMatrix[self.getPLTIndex, :]

    def SortResults(self, Col=None):
        """
        Sorts the differents values by a given column.

        Improvements:
        - Add the possibility to extract the values directly from the pltDataMatrix
        """
        # Verify that the index selection array is not empty
        if self.getPLTIndex is None:
            print("Error: No index selected.")
            return False

        # Select the column to sort by
        if Col is None:
            if self.getSelectCol is None:
                print("Error: No column selected.")
                return False
            Col = self.getSelectCol

        # Sort the data
        # Extract the values to sort by
        ArrayExtratedVal = self.getDataMatrix[self.getPLTIndex, Col]

        # Sort the PLTIndex array by the values in the selected column
        IndexOrder = np.argsort(ArrayExtratedVal)
        self.getPLTIndex = self.getPLTIndex[IndexOrder]

        # Sort the PLTDataMatrix
        if self.getPLTDataMatrix is not None:
            self.getPLTDataMatrix = self.getDataMatrix[IndexOrder, :]
        else:
            self.getPLTDataMatrix = self.getDataMatrix[IndexOrder, :]

    def PLTPreprocessing(self):
        """
        Preprocesses data for plotting by putting them into the right variables.
        """
        # Verify that the index selection array is not empty
        if self.getPLTIndex is None:
            print("Warning: No index selected. Resetting the index.")
            self.ResetPLTIndex

        if self.getAbsCol is None:
            print("Error: No abscissa column selected.")
            return False

        if self.getOrdCol is None:
            print("Error: No ordinate column selected.")
            return False

        # Extract the data to plot
        # Extract the abscissa
        self.getAbsVal = self.getDataMatrix[self.getPLTIndex, self.getAbsCol]

        # Extract the ordinate
        self.getOrdVal = self.getDataMatrix[self.getPLTIndex, self.getOrdCol]

        # Extract the time
        if self.getTimeCol is not None:
            self.getTimeVal = self.getDataMatrix[self.getPLTIndex, self.getTimeCol]
        else:
            self.getTimeVal = None
            print("Warning: No time column selected.")

    def TimeStep2Time(self):
        pass
        # permet de faire la traduction de time step ? un temps

        # S'aider de la colonne de unique time step

    def Time2TimeStep(self):
        pass
        # permet de faire la traduction de temps ? un time step

        # S'aider de la colonne de unique time step

    def CMPTFunctionPerTimeStep(self, Func, AbsTol=0.0001):
        """
        Function that apply a function to a given column per time step

        Args:
            Func (function): Function to apply to the data.
            AbsTol (float): Absolute tolerance for time selection.

        Returns:
            BoolSuccess (bool): True if the function was applied successfully, otherwise False.

        """
    
        # Verify that the data matrix is not empty
        if self.getDataMatrix is None:
            print("Error: No data matrix.")
            return False

        # Verify that the time column is selected
        if self.getTimeCol is None:
            print("Error: No time column selected.")
            return False

        # Verify that the ordinate column is selected
        if self.getOrdCol is None:
            print("Error: No ordinate column selected.")
            return False

        # Extract the unique time steps
        UniqueTimeSteps, NTimeSteps = self.getUniqueTimeSteps

        # List to store the results
        for Time in UniqueTimeSteps:
            # Select the data for the given time step
            self.ResetPLTIndex
            self.SelectTime(Val=Time, AbsTol=AbsTol)
            self.PLTPreprocessing()

            # Apply the function to the selected data
            Func(self)

        return True


"""
-Improvement to be done:
- Add the possibility to extract the values directly from the pltDataMatrix
- Add the capability to use the data of different files at the same time
    - Add the ability to merge the data of different files
"""
# Fonction import de donn?
# Fonction de traitement des donn?es
# Fonction d'affichage
# Fonction d'export de donn?e
