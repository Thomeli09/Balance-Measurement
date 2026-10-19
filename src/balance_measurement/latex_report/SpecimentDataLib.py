# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Module for managing specimen metadata and test information


# Other Lib
from datetime import datetime


# Custom Lib


"""
Specimen Data Module

# Improvement to be done:
- 
"""


class SpecimenData:
    def __init__(self, Project: str, SpecimenID: str, Material: str, GeometryDimensions: str,
                ManufacturingProcess: str, TestID: str, TestType: str, Measurement: str, 
                Environment: str, Machine: str, Operator:str, Date: list[datetime]):
        # Metadata
        self._Project = Project # Project associated with the balance
        self._SpecimenID = SpecimenID # Unique identifier of the specimen being measured
        self._Material = Material # Material being measured (e.g., cement, aggregate, etc.)
        self._GeometryDimensions = GeometryDimensions # Geometry dimensions of the specimen (e.g., length, width, height, etc.)
        self._ManufacturingProcess = ManufacturingProcess # Manufacturing process of the specimen (e.g., mixing, curing, etc.)
        self._TestID = TestID # Unique identifier of the test being performed
        self._TestType = TestType # Type of test being performed (e.g., compression, tension, etc.)
        self._Measurement = Measurement # Measurement value obtained from the test
        self._Environment = Environment # Environmental conditions during the test (e.g., temperature, humidity, etc.)
        self._Machine = Machine # Machine used for the test (e.g., Mettler, A&D, etc.)
        self._Operator = Operator # Operator performing the test
        self._Date = Date # Start and end date of the test (TimeObject)

    # Metadata
    @property
    def getProject(self) -> str:
        return self._Project

    @getProject.setter
    def getProject(self, Project: str) -> None:
        self._Project = Project

    @property
    def getSpecimenID(self) -> str:
        return self._SpecimenID

    @getSpecimenID.setter
    def getSpecimenID(self, SpecimenID: str) -> None:
        self._SpecimenID = SpecimenID

    @property
    def getMaterial(self) -> str:
        return self._Material

    @getMaterial.setter
    def getMaterial(self, Material: str) -> None:
        self._Material = Material

    @property
    def getGeometryDimensions(self) -> str:
        return self._GeometryDimensions

    @getGeometryDimensions.setter
    def getGeometryDimensions(self, GeometryDimensions: str) -> None:
        self._GeometryDimensions = GeometryDimensions

    @property
    def getManufacturingProcess(self) -> str:
        return self._ManufacturingProcess

    @getManufacturingProcess.setter
    def getManufacturingProcess(self, ManufacturingProcess: str) -> None:
        self._ManufacturingProcess = ManufacturingProcess

    @property
    def getTestID(self) -> str:
        return self._TestID

    @getTestID.setter
    def getTestID(self, TestID: str) -> None:
        self._TestID = TestID

    @property
    def getTestType(self) -> str:
        return self._TestType

    @getTestType.setter
    def getTestType(self, TestType: str) -> None:
        self._TestType = TestType

    @property
    def getMeasurement(self) -> str:
        return self._Measurement

    @getMeasurement.setter
    def getMeasurement(self, Measurement: str) -> None:
        self._Measurement = Measurement

    @property
    def getEnvironment(self) -> str:
        return self._Environment

    @getEnvironment.setter
    def getEnvironment(self, Environment: str) -> None:
        self._Environment = Environment

    @property
    def getMachine(self) -> str:
        return self._Machine

    @getMachine.setter
    def getMachine(self, Machine: str) -> None:
        self._Machine = Machine

    @property
    def getOperator(self) -> str:
        return self._Operator

    @getOperator.setter
    def getOperator(self, Operator: str) -> None:
        self._Operator = Operator

    @property
    def getDate(self) -> datetime:
        return self._Date

    @getDate.setter
    def getDate(self, Date: datetime) -> None:
        self._Date = Date
