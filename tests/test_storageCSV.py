# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Test the data storage functionality of the module

# Other Lib




"""
.CSV files
Implementation status: OK
"""
# Object creation
CSVData = StorageCSV(FilePath="TestDataStorage.csv", FieldNames=["Key", "date", "value 1", "value 2"], BBackupFile=True)

# Data addition
CSVData.DataAppend(Key=1, Value=["2026-08-11", 1, 2])
CSVData.DataAppend(Key=2, Value=["2026-08-12", 3, 4])
CSVData.DataAppend(Key=3, Value=["2026-08-13", 5, 6])

# Write the data to the CSV file
CSVData.Write()

# Append data to the CSV file and data structure
DictAppendData = {4: ["2026-08-14", 7, 8], 5: ["2026-08-15", 9, 10]}
CSVData.Append(Data=DictAppendData)

# Generate a reading object to read the data from the CSV file
CSVDataRead = StorageCSV(FilePath="TestDataStorage.csv")

# Read the data from the CSV file
CSVDataRead.Read()
print(CSVDataRead.getData)

# Write the data to a new CSV file with specified field types
CSVData.getFilePath = "TestDataStorageUnit.csv"
CSVData.getFieldNames = None
CSVData.getFieldTypes = ["int", "str", "float", "float"]

# Write the data to the new CSV file
CSVData.Write()

# Read the data from the new CSV file with specified field types
CSVDataReadUnit = StorageCSV(FilePath="TestDataStorageUnit.csv")
CSVDataReadUnit.Read()
print(CSVDataReadUnit.getData)


from balance_measurement import StorageCSV


def test_csv_measurements_round_trip(tmp_path):
    path = tmp_path / "measurements.csv"
    storage = StorageCSV(
        FilePath=path,
        FieldNames=["id", "weight"],
        FieldTypes=["int", "float"],
    )
    storage.DataAppend(Key=1, Value=[12.5])
    storage.Write()

    loaded = StorageCSV(FilePath=path)
    assert loaded.Read() == {1: [12.5]}