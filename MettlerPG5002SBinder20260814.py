# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Essai de l'utilisation de la balance Mettler PG5002S dans une binder


# Other Lib
import datetime
import time


# Custom Lib
import TimeLib 

from SpecimentDataLib import SpecimenData

from ScaleBench import SerialScale, AutoReconSerialScale, Scale

from DataStorageLib import Storage, StorageCSV
from GUIMessageLib import LogManager

from PlotLib import ParamPLT

from BalanceLib import BalanceBasic, Balance


if __name__ == "__main__":

    Msg = LogManager(Name="ScaleApp", LogFile="scale_app.log")

    Msg.getLevel = 0

    Msg.LoggerConfiguration()

    Metadata = SpecimenData(Project="Thèse THOMMES Eliott", SpecimenID="", Material="", GeometryDimensions="", ManufacturingProcess="", 
                            TestID="", TestType="Évolution de la masse au cours du temps en raison des courants d'air", 
                            Measurement="Évolution de la masse au cours du temps", Environment="Température et humidité relative régulées", 
                            Machine="Mettler PG5002-S et Binder", Operator="THOMMES Eliott", Date=["14/08/2026"])

    CSVData = StorageCSV(FilePath="MettlerPG5002SBinder20260814-4.csv", FieldNames=["Key", "Date", "Command", "Status", "Value", "Unit"], 
                         FieldTypes=["int", "str", "str", "str", "float", "str"], BBackupFile=True, Logger=Msg)

    scale = Scale(Port="COM3", Baudrate = 9600, Timeout = 2.0, BAutoReconnect = False,
                 Protocol=1, Logger=Msg)

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

    BalanceMettlerPG = Balance(BalanceSerial=scale, Name="MettlerPG5002SBinder20260814-1", ID=None, SpecimenData=Metadata, 
                            Colour=None, Hatch=None, ParamPLT=None, 
                            Unit="g", DataStorage=CSVData, Logger=Msg, 
                            SerialPort=None, Baudrate=None, BRecord=False)
    
    BalanceMettlerPG.getWeight()

    Waiting = 30
    print(f"Waiting {Waiting} seconds before starting the repeated measurement.\nPlace a weight on the scale and ensure it is stable.") 
    time.sleep(Waiting)

    MeasurementDuration = 4*60 # 1 hour
    Delay = 0.4 # seconds
    print(f"Starting the repeated measurement during {MeasurementDuration/60} minutes with a delay of {Delay} seconds between each measurement.")

    NumRead = int(MeasurementDuration/Delay)
    MeasurementList = BalanceMettlerPG.getWeightRepeated(NumRead=NumRead, Delay=Delay, DelayMode='Variable')

    CSVData.Write()

    print("Measurement completed. Disconnecting the scale.")

    scale.Disconnect()

    Msg.Shutdown()