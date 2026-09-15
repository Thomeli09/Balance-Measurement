# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Balance module for measuring balance in various contexts


# Other Lib

import time

# Custom Lib
from SpecimentDataLib import SpecimenData

from ScaleBench import SerialScale, AutoReconSerialScale, Scale

import TimeLib 
import datetime

from DataStorageLib import Storage, StorageCSV
from GUIMessageLib import LogManager

from PlotLib import ParamPLT
"""
@dataclass
class MessageEntry:
    ID: int
    Sample: str
    Timestamp: datetime
    Stability: bool
    Balance: str
    Weight: float
    Message: str
"""

"""
Balance Measurement Module

# Improvement to be done:
- Faire passer la rallonge par le trou ou par la porte (coin)
"""

class BalanceBasic:
    def __init__(self, Name: str | None = None, ID: str | None = None, 
                 SpecimenData: SpecimenData | None = None, Colour: str | None = None, 
                 Hatch: str | None = None, ParamPLT: ParamPLT | None = None, 
                 Unit: str | None = None, DataStorage: Storage | None = None, 
                 Logger: LogManager | None = None):

        # Metadata
        # Metadata : Balance
        self._Name: str = Name # Name of the Balance
        self._ID = ID # Unique identifier of the balance

        # Metadata Specimen
        self._SpecimenData = SpecimenData # SpecimenDataSheet object containing metadata about the specimen being measured

        # Graphics
        self._Colour = Colour
        self._Hatch = Hatch
        self._ParamPLT = ParamPLT

        # Parameters of the balance measurement
        self._Unit = Unit # Unit of measurement (e.g., grams, kilograms, etc.)

        # Data
        self._DataStorage = DataStorage  # Data log of the balance measurements

        # Logger and debug
        self._Logger = None

    # Metadata

    # Metadata : Balance
    @property
    def getName(self):
        return self._Name

    @getName.setter
    def getName(self, Name) -> None:
        self._Name = Name

    @property
    def getID(self):
        return self._ID

    @getID.setter
    def getID(self, ID):
        self._ID = ID

    # Metadata : Specimen
    @property
    def getSpecimenData(self):
        return self._SpecimenData

    @getSpecimenData.setter
    def getSpecimenData(self, SpecimenData):
        self._SpecimenData = SpecimenData

    # Graphics
    @property
    def getColour(self):
        return self._Colour

    @getColour.setter
    def getColour(self, Colour):
        self._Colour = Colour

    @property
    def getHatch(self):
        return self.Hatch

    @getHatch.setter
    def getHatch(self, Hatch):
        self._Hatch = Hatch

    @property
    def getParamPLT(self):
        return self._ParamPLT

    @getParamPLT.setter
    def getParamPLT(self, ParamPLT):
        self._ParamPLT = ParamPLT

    # Parameters of the balance measurement
    @property
    def getUnit(self):
        return self._Unit

    @getUnit.setter
    def getUnit(self, Unit):
        self._Unit = Unit

    # Data
    @property
    def getDataStorage(self):
        return self._DataStorage

    @getDataStorage.setter
    def getDataStorage(self, DataStorage):
        self._DataStorage = DataStorage

    # Logger and debug
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


class BalanceManager(BalanceBasic):
    def __init__(self, Name: str | None = None, ID: str | None = None, 
                 SpecimenData: SpecimenData | None = None, Colour: str | None = None, 
                 Hatch: str | None = None, ParamPLT: ParamPLT | None = None, 
                 Unit: str | None = None, DataStorage: Storage | None = None, 
                 Logger: LogManager | None = None):

        super().__init__(Name=Name, ID=ID, SpecimenData=SpecimenData, Colour=Colour, 
                         Hatch=Hatch, ParamPLT=ParamPLT, Unit=Unit, DataStorage=DataStorage, 
                         Logger=Logger)

        # Parameters of the balance measurement

        # Multiple Balance Management

        # Multiple Balance Management : Balances
        self.LBalance = None  # List of Balance objects to be used in the module
        
        # Multiple Balance Management : Parameters

    # Parameters of the balance measurement

    # Multiple Balance Management

    # Multiple Balance Management : Balances
    @property
    def getLBalance(self):
        return self.LBalance

    @getLBalance.setter
    def getLBalance(self, LBalance):
        if isinstance(LBalance, Balance):
            if self.LBalance is None:
                self.LBalance = [LBalance]
            else:
                self.LBalance.append(LBalance)
        elif isinstance(LBalance, list) and all(isinstance(b, Balance) for b in LBalance):
            self.LBalance = LBalance
        else:
            raise ValueError("LBalance must be a Balance instance or a list of Balance instances")
        
    # Multiple Balance Management : Parameters


class Balance(BalanceBasic):
    def __init__(self, BalanceSerial:SerialScale | AutoReconSerialScale | Scale, Name: str | None = None, ID: str | None = None, 
                 SpecimenData: SpecimenData | None = None, Colour: str | None = None, 
                 Hatch: str | None = None, ParamPLT: ParamPLT | None = None, 
                 Unit: str | None = None, DataStorage: Storage | None = None, 
                 Logger: LogManager | None = None, SerialPort: str | None = None, Baudrate: int | None = None, BRecord: bool = False):

        super().__init__(Name=Name, ID=ID, SpecimenData=SpecimenData, Colour=Colour,
                         Hatch=Hatch, ParamPLT=ParamPLT, Unit=Unit, DataStorage=DataStorage, 
                         Logger=Logger)

        # Communication Management
        self._BalanceSerial = BalanceSerial  # Serial connection object for the balance

        # Communication Parameters
        self._SerialPort = None  # Serial port for communication
        self._BaudRate = None  # Baud rate for serial communication

        # Parameters of the balance measurement
        self._IndexMeasure: int = 0  # Index of the current measurement

        # Plotting Parameters

        # Record and display Parameters
        self._BRecord = BRecord  # Boolean to control recording of balance measurements
        self._BDisplayRealTimePrint = False  # Boolean to control printing of balance measurements in real-time
        self._BDisplayRealTimePlot = False  # Boolean to control real-time plotting of balance measurements


        # Preparation of the object
        self.getSerialPort = self.getBalanceSerial.getSerialPort if SerialPort is None else SerialPort
        self.getBaudRate = self.getBalanceSerial.getBaudrate if Baudrate is None else Baudrate


    # Communication Management
    @property
    def getBalanceSerial(self) -> SerialScale | AutoReconSerialScale | Scale:
        return self._BalanceSerial

    @getBalanceSerial.setter
    def getBalanceSerial(self, BalanceSerial: SerialScale | AutoReconSerialScale | Scale) -> None:
        self._BalanceSerial = BalanceSerial

    # Communication Parameters
    @property
    def getSerialPort(self):
        return self._SerialPort

    @getSerialPort.setter
    def getSerialPort(self, SerialPort):
        if not isinstance(SerialPort, str):
            print("Error: SerialPort must be a string.")
            return
        self._SerialPort = SerialPort

    @property
    def getBaudRate(self):
        return self._BaudRate

    @getBaudRate.setter
    def getBaudRate(self, Baudrate):
        if not isinstance(Baudrate, int):
            print("Error: Baudrate must be an integer.")
            return
        self._BaudRate = Baudrate

    # Parameters of the balance measurement
    @property
    def getIndexMeasure(self) -> int:
        return self._IndexMeasure

    @getIndexMeasure.setter
    def getIndexMeasure(self, IndexMeasure: int) -> None:
        if not isinstance(IndexMeasure, int):
            print("Error: IndexMeasure must be an integer.")
            return
        self._IndexMeasure = IndexMeasure

    @property
    def ResetIndexMeasure(self) -> None:
        self.getIndexMeasure = 0

    # Plotting Parameters


    # Display Parameters
    @property
    def getBRecord(self) -> bool:
        return self._BRecord

    @getBRecord.setter
    def getBRecord(self, BRecord: bool) -> None:
        if not isinstance(BRecord, bool):
            print("Error: BRecord must be a boolean.")
            return
        self._BRecord = BRecord

    @property
    def getBDisplayRealTimePrint(self) -> bool:
        return self._BDisplayRealTimePrint

    @getBDisplayRealTimePrint.setter
    def getBDisplayRealTimePrint(self, BDisplayRealTimePrint: bool) -> None:
        if not isinstance(BDisplayRealTimePrint, bool):
            print("Error: BDisplayRealTimePrint must be a boolean.")
            return
        self._BDisplayRealTimePrint = BDisplayRealTimePrint

    @property
    def getBDisplayRealTimePlot(self) -> bool:
        return self._BDisplayRealTimePlot

    @getBDisplayRealTimePlot.setter
    def getBDisplayRealTimePlot(self, BDisplayRealTimePlot: bool) -> None:
        if not isinstance(BDisplayRealTimePlot, bool):
            print("Error: BDisplayRealTimePlot must be a boolean.")
            return
        self._BDisplayRealTimePlot = BDisplayRealTimePlot
    
    
    # Measurement management
    def ListPrefix(self, ListOriginal: list | list[list], Prefixes: list | list[list]) -> list | list[list] | None:
        """
        Add prefix to lists.
        This method can be overridden in subclasses to implement specific prefix steps.
        """
        if isinstance(ListOriginal, list) and isinstance(Prefixes, list):
            if all(isinstance(SubList, list) for SubList in ListOriginal):
                if all(isinstance(Prefix, list) for Prefix in Prefixes):
                    return [self.ListPrefix(ListOriginal=SubList, Prefixes=Prefix) for SubList, Prefix in zip(ListOriginal, Prefixes)]
                else:
                    return [self.ListPrefix(ListOriginal=SubList, Prefixes=Prefixes) for SubList in ListOriginal]
            else:
                # If ListOriginal is a single list, add prefix to it
                if all(isinstance(Prefix, list) for Prefix in Prefixes) and Prefixes:
                    return Prefixes[0] + ListOriginal
                else:
                    return Prefixes + ListOriginal
        else:
            print("Error: ListOriginal must be a list or a list of lists.")
            return None

    def ListSuffix(self, ListOriginal: list | list[list], Suffixes: list | list[list]) -> list | list[list] | None:
        """
        Add suffix to lists.
        This method can be overridden in subclasses to implement specific suffix steps.
        """
        if isinstance(ListOriginal, list) and isinstance(Suffixes, list):
            if all(isinstance(SubList, list) for SubList in ListOriginal):
                if all(isinstance(Suffix, list) for Suffix in Suffixes):
                    return [self.ListSuffix(ListOriginal=SubList, Suffixes=Suffix) for SubList, Suffix in zip(ListOriginal, Suffixes)]
                else:
                    return [self.ListSuffix(ListOriginal=SubList, Suffixes=Suffixes) for SubList in ListOriginal]
            else:
                # If ListOriginal is a single list, add suffix to it
                if all(isinstance(Suffix, list) for Suffix in Suffixes)  and Suffixes:
                    return ListOriginal + Suffixes[0]
                else:
                    return ListOriginal + Suffixes
        else:
            print("Error: ListOriginal must be a list or a list of lists.")
            return None

    def MeasurePreparation(self, Measurements: list, Suffixes: list = []) -> list | None:
        """
        Prepare the balance for measurement.
        This method can be overridden in subclasses to implement specific preparation steps.
        """
        if isinstance(Measurements, list) and isinstance(Suffixes, list):
            Date = datetime.datetime.now()
            DateString = Date.isoformat(sep=" ", timespec="milliseconds")

            Measurements = self.ListPrefix(ListOriginal=Measurements, Prefixes=[self.getIndexMeasure, DateString])
            self.getIndexMeasure += 1
            Measurements = self.ListSuffix(ListOriginal=Measurements, Suffixes=Suffixes)
            return Measurements
        else:
            print("Error: Measurements must be a list or a list of lists.")
            return None

    def MeasureStorage(self, Measurement: list) -> None:
        """
        Store the balance measurements.
        This method can be overridden in subclasses to implement specific storage steps.
        """
        if self.getDataStorage is not None:
            if self.getBRecord:
                DictAppendData = {Measurement[0]: Measurement[1:]}
                self.getDataStorage.Append(Data=DictAppendData)
            else:
                self.getDataStorage.DataAppend(Key=Measurement[0], Value=Measurement[1:])
        else:
            print("Error: DataStorage is not set.")
            return None
        
    # Balance Connection
    @property
    def setBalanceConnect(self):
        """
        Create a new instance of SerialScale to establish a connection with the balance.
        """
        if self.getPort is None or self.getBaudRate is None:
            print("Error: Port and Baudrate must be set before establishing a connection.")
            return
        try:
            self.getBalanceSerial = SerialScale(port=self.getPort, baudrate=self.getBaudRate)
            print(f"Successfully connected to balance on port {self.getPort} with baud rate {self.getBaudRate}.")
        except Exception as e:
            print(f"Error connecting to balance: {e}")

    @property
    def setBalanceReConnect(self):
        """
        Create a new instance of AutoReconnectSerialScale to re-establish the connection with the balance automatically if it gets disconnected. 
        This is useful for maintaining a stable connection during long measurement sessions.
        """
        if self.getPort is None or self.getBaudRate is None:
            print("Error: Port and Baudrate must be set before establishing a connection.")
            return
        try:
            self.getBalanceSerial = AutoReconSerialScale(port=self.getPort, baudrate=self.getBaudRate)
            print(f"Successfully reconnected to balance on port {self.getPort} with baud rate {self.getBaudRate}.")
        except Exception as e:
            print(f"Error reconnecting to balance: {e}")

    # Generic Balance Method
    def getWeight(self) -> list | None:
        """
        Measure the weight using the balance.
        Returns:
            float: A value representing the weight measured by the balance.
        """
        if not self.getBConnected():
            print("Error: Balance connection is not established.")
            return None
        try:
            Measure = self.getBalanceSerial.getWeight()

            Measurement = self.MeasurePreparation(Measure)
            self.MeasureStorage(Measurement=Measurement)

            return Measurement

        except Exception as e:
            print(f"Error measuring weight: {e}")
            return None

    def getWeightStable(self, NumRead: int, Delay: float, TimeOut: float, AbsTol: float, RelTol: float) -> list | None:
        """
        Measure the weight multiple times until a stable value is reached within a specified tolerance.
        Args:
            NumRead (int): Number of measurements to take.
            Delay (float): Delay between measurements in seconds.
            Tolerance (float): Tolerance for stability.
        Returns:
            float: The stable weight measurement.
        """
        Weights = []

        BoolContinue = True
        PreWeight = 0

        IndexRead = 0
        Deadline = time.time() + TimeOut

        while BoolContinue:
            Weight = self.getWeight()

            if Weight is not None:
                IndexRead += 1
                Weights.append(Weight)
            else:
                print("Error: Failed to measure weight.")
                return None

            if IndexRead >= NumRead:
                BoolContinue = False
            elif time.time() > Deadline:
                BoolContinue = False
            elif abs(Weight - PreWeight) < AbsTol and abs(Weight - PreWeight) / abs(PreWeight) < RelTol:
                BoolContinue = False # Mettre une autre condition de convergence se baser sur l'analyse des données précédentes pour déterminer si ok
                # Mettre un délai pour vérifier la convergence
            PreWeight = Weight
            time.sleep(Delay)

        StableWeight = sum(Weights) / len(Weights) # Calculer d'une autre manière la valeur stable en fonction des données précédentes pour déterminer si ok
        # Par exemple ne pas utiliser les zones ou varie de trop les outliers et avant pas converger
        return StableWeight

    def getWeightRepeated(self, NumRead: int, Delay: float, DelayMode: str | int = 'fixed'):
        """
        Measure the weight multiple times with a specified delay between measurements.
        Args:
            NumRead (int): Number of measurements to take.
            Delay (float): Delay between measurements in seconds.
        Returns:
            list: A list of weight measurements.

        Improovement to be done:
        - Add a variable delay option to allow for dynamic adjustment of the delay to fit the specified delay between measurements. 
        This would allow to take into account the save time of the measurement, sois sur base du pas précédent et du moment avant la mesure plus le délai et
        l'heure actuelle après sauvegarde de la mesure pour déterminer le délai à appliquer pour la prochaine mesure et indiquer les statistiques et si délai trop bas
        négatif
        """
        DelayModeDict = {'Fixed': 'Fixed', 'Variable': 'Variable', 
                         0: 'Fixed', 1: 'Variable'}

        DelayMode = DelayModeDict.get(DelayMode, 'Fixed')  # Default to 'Fixed' if unknown mode is provided

        Measurements = []

        if DelayMode == 'Fixed':  # Fixed minimum delay mode
            for _ in range(NumRead):
                Measurement = self.getWeight()

                if Measurement is not None:
                    Measurements.append(Measurement)
                else:
                    print("Error: Failed to measure weight.")
                    return Measurements
                
                time.sleep(Delay)
        else:  # Variable delay mode
            for _ in range(NumRead):
                TimeBe4Measure = time.time() # Time before the measurement

                Measurement = self.getWeight()

                if Measurement is not None:
                    Measurements.append(Measurement)
                else:
                    print("Error: Failed to measure weight.")
                    return Measurements

                TimeAfterMeasure = time.time() # Time after the measurement is taken

                ElapsedTime = TimeAfterMeasure - TimeBe4Measure
                AdjustedDelay = max(0, Delay - ElapsedTime)

                time.sleep(AdjustedDelay)

        return Measurements

    def getWeightReliable(self, NumRead: int, Delay: float, Method='Average'):
        """
        Measure the weight multiple times and return the most reliable measurement based on the specified method (Average, Median, etc.).
        Args:
            NumRead (int): Number of measurements to take.
            Delay (float): Delay between measurements in seconds.
            Method (str): Method to determine the most reliable measurement ('Average' or 'Median').
        """
        DictMethods = {'Average': 'Average', 'Median': 'Median',
                       0: 'Average', 1: 'Median'}

        Method = DictMethods.get(Method, 'Average')  # Default to 'Average' if unknown method is provided

        Weights = self.getWeightRepeated(NumRead=NumRead, Delay=Delay)
        if not Weights:
            print("Error: No weight measurements were taken.")
            return None
        if Method == 'Average':
            ReliableWeight = sum(Weights) / len(Weights)
        elif Method == 'Median':
            ReliableWeight = sorted(Weights)[len(Weights) // 2]
        else:
            print(f"Error: Unknown method '{Method}'. Use 'Average' or 'Median'.")
            return None
        return ReliableWeight
 
    def setTare(self, Value: float = 0.0) -> None:
        """
        Tare the balance to zero or a specific value.
        """
        if Value != 0.0:
            self.setTareValue(Value)
        else:
            if not self.getBConnected():
                print("Error: Balance connection is not established.")
                return None
            try:
                self.getBalanceSerial.Tare()
                print("Balance tared successfully.")
            except Exception as e:
                print(f"Error taring balance: {e}")

    def setTareValue(self, value: float = 0.0) -> None:
        """
        Set the tare value of the balance to a specific value.
        Args:
            value (float): The value to set as the tare.
        """
        if not self.getBConnected():
            print("Error: Balance connection is not established.")
            return None
        try:
            self.getBalanceSerial.setTare(value)
            print(f"Balance tared to {value} successfully.")
        except Exception as e:
            print(f"Error setting tare value: {e}")

    def setZero(self):
        """
        Zero the balance.
        """
        if not self.getBConnected():
            print("Error: Balance connection is not established.")
            return None
        try:
            self.getBalanceSerial.Zero()
            print("Balance zeroed successfully.")
        except Exception as e:
            print(f"Error zeroing balance: {e}")

    def getBConnected(self):
        """
        Check if the balance is connected.
        Returns:
            bool: True if the balance is connected, False otherwise.
        """
        if self.getBalanceSerial is None:
            return False
        else:
            return self.getBalanceSerial.getBConnected()

    def getBResponsive(self):
        """
        Check if the balance is responsive.
        Returns:
            bool: True if the balance is responsive, False otherwise.
        """
        if self.getBalanceSerial is None:
            return False
        else:
            return self.getBalanceSerial.getBResponsive()

    # Closing the object
    def Disconnect(self):
        """
        End the connection with the balance.
        """
        if not self.getBConnected():
            print("Error: Balance connection is not established.")
            return None
        try:
            self.getBalanceSerial.Disconnect()
            self.getBalanceSerial = None
            print("Balance connection closed successfully.")
        except Exception as e:
            print(f"Error closing balance connection: {e}")

class BalanceMettler(Balance):
    def __init__(self):
        super().__init__()
        # Mettler specific data and parameters

    # Mettler specific data and parameters

    # Mettler specific methods
    def getMeasurement(self):
        """
        Measure the balance using Mettler-specific logic.
        Args:
            data: The input data to measure balance.
        Returns:
            float: A value representing the balance of the data.
        """
        # Implement Mettler-specific balance measurement algorithm here
        balance_value = 0.0  # Replace with actual computation
        return balance_value


class BalanceAD(Balance):
    def __init__(self):
        super().__init__()
        # A&D specific data and parameters

    # A&D specific data and parameters

    # A&D specific methods
    def getMeasurement(self):
        """
        Measure the balance using A&D-specific logic.
        Args:
            data: The input data to measure balance.
        Returns:
            float: A value representing the balance of the data.
        """
        # Implement A&D-specific balance measurement algorithm here
        balance_value = 0.0  # Replace with actual computation
        return balance_value


