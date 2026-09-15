# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Example of usage of the balance measurement module


# Other Lib
import datetime
import time


# Custom Lib
import TimeLib 

from SpecimentDataLib import SpecimenData

from ScaleBench import SerialScale, AutoReconSerialScale, Scale

from DataStorageLib import Storage, StorageCSV
from GUIMessageLib import MessageManager

from PlotLib import ParamPLT

from BalanceLib import BalanceBasic, Balance


if __name__ == "__main__":

    AggregatesData = SpecimenData(Project="Test", SpecimenID="NA1", Material="Concrete", GeometryDimensions="Aggregates",
                ManufacturingProcess="", TestID="", TestType="", Measurement="Drying weight", 
                Environment="", Machine="Binder", Operator="THOMMES Eliott", Date=[f"{datetime.datetime.now()}"])

    CSVData = StorageCSV(FilePath="MeasurementNATest.csv", FieldNames=["Key", "Date", "Command", "Status", "Value", "Unit"], 
                         FieldTypes=["int", "str", "str", "str", "float", "str"], BBackupFile=False)

    scale = Scale(Port="COM3", Baudrate = 9600, Timeout = 2.0, BAutoReconnect = False,
                 Protocol=1)

    scale.Start()

    if scale.getBConnected():
        print("Scale is connected.")
        scale.Zero() # Zero the scale all the time before measuring
        if scale.getBResponsive():
            print("Scale is responsive.")
        else:
            print("Scale is unresponsive.")
    else:
        print("Scale not connected.")

    BalanceTestNA = Balance(BalanceSerial=scale, 
                            Name=None, ID=None, SpecimenData=AggregatesData, 
                            Colour=None, Hatch=None, ParamPLT=None, 
                            Unit=None, DataStorage=CSVData, 
                            MessageHDL=None, SerialPort=None, Baudrate=None, BRecord=True)
    
    BalanceTestNA.getWeight()

    Waiting = 10
    print(f"Waiting {Waiting} seconds before starting the repeated measurement.\nPlace a weight on the scale and ensure it is stable.") 
    time.sleep(Waiting)

    print("Starting the repeated measurement.")

    MeasurementList = BalanceTestNA.getWeightRepeated(NumRead=10, Delay=0.5, DelayMode='Variable')

    print("Measurement completed. Disconnecting the scale.")
    
    BalanceTestNA.getWeight()

    scale.Disconnect()
