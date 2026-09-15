# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Scale Bench library


# Other Lib
import re

import statistics

import time
from datetime import datetime

import serial
from serial import SerialException


# Custom Lib
from GUIMessageLib import LogManager

import TimeLib


"""
Balance Measurement Module

# Improvement to be done:
- Additional error handling for serial communication issues.
- Support for more scale protocols if needed.
- utile affichage pour dire en utilisation sur la balance
"""

class SerialScale:
    """ Standard low-level serial scale driver for RS-232/USB bench scales.

    Handles raw command/response exchange and protocol detection.
    """

    def __init__(self, Port: str, Baudrate: int = 9600, Timeout: float = 1,
        Protocol: int | None = None, Logger: LogManager | None = None):
        """Open the serial port and detect the scale protocol.

        Args:
            Port: Serial device path, e.g. "/dev/ttyUSB0" or "COM3".
            Baudrate: Baud rate matching the scale's RS-232 setting.
            Timeout: Per-readline timeout in seconds.
            Protocol: Force protocol 1 (multi-line) or 2 (single-line).
                Omit to auto-detect on first connection.
        """
        # Connection parameters
        self._SerialPort = Port
        self._Baudrate = Baudrate
        self._ByteSize = serial.EIGHTBITS
        self._Parity = serial.PARITY_NONE
        self._StopBits = serial.STOPBITS_ONE
        self._Timeout = Timeout

        # Communication protocol (1, 2...) or None for auto-detection
        self._Protocol: int | None = Protocol
        self._InterTimeCom: float = 0.1  # Minimum time between commands and responses in seconds

        # Communication manager
        self._ComSerial = serial.Serial(port=self._SerialPort,
            baudrate=self._Baudrate,
            bytesize=self._ByteSize,
            parity=self._Parity,
            stopbits=self._StopBits,
            timeout=self._Timeout)

        # Communication data
        self._LastResponseTime: datetime | None = None

        # Logger and debug
        self._Logger = None
        self._BDebug: bool = False

        # Scale preparation: clear buffers and detect protocol
        self.getComSerial.reset_input_buffer()
        self.getComSerial.reset_output_buffer()
        #self.getInferedProtocol()

    # Connection parameters
    @property
    def getSerialPort(self) -> str:
        return self._SerialPort

    @getSerialPort.setter
    def getSerialPort(self, Port: str) -> None:
        self._SerialPort = Port

    @property
    def getBaudrate(self) -> int:
        return self._Baudrate

    @getBaudrate.setter
    def getBaudrate(self, Baudrate: int) -> None:
        self._Baudrate = Baudrate

    @property
    def getByteSize(self) -> int:
        return self._ByteSize

    @getByteSize.setter
    def getByteSize(self, ByteSize: int) -> None:
        self._ByteSize = ByteSize

    @property
    def getParity(self) -> str:
        return self._Parity

    @getParity.setter
    def getParity(self, Parity: str) -> None:
        self._Parity = Parity

    @property
    def getStopBits(self) -> int:
        return self._StopBits

    @getStopBits.setter
    def getStopBits(self, StopBits: int) -> None:
        self._StopBits = StopBits

    @property
    def getTimeout(self) -> float:
        return self._Timeout

    @getTimeout.setter
    def getTimeout(self, Timeout: float) -> None:
        self._Timeout = Timeout

    # Communication protocol
    @property
    def getProtocol(self) -> int | None:
        return self._Protocol

    @getProtocol.setter
    def getProtocol(self, Protocol: int | None) -> None:
        self._Protocol = Protocol

    @property
    def getInterTimeCom(self) -> float:
        return self._InterTimeCom

    @getInterTimeCom.setter
    def getInterTimeCom(self, InterTimeCom: float) -> None:
        self._InterTimeCom = InterTimeCom

    # Communication manager
    @property
    def getComSerial(self) -> serial.Serial:
        return self._ComSerial

    @getComSerial.setter
    def getComSerial(self, ComSerial: serial.Serial) -> None:
        self._ComSerial = ComSerial

    # Communication data
    @property
    def getLastResponseTime(self) -> datetime | None:
        return self._LastResponseTime

    @getLastResponseTime.setter
    def getLastResponseTime(self, LastResponseTime: datetime | None) -> None:
        self._LastResponseTime = LastResponseTime

    def setLastResponseTime(self, LastResponseTime: datetime | None = None) -> None:
        if LastResponseTime is None:
            self._LastResponseTime = datetime.utcnow()
        else:
            self.getLastResponseTime = LastResponseTime

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

    @property
    def getBDebug(self) -> bool:
        return self._BDebug

    @getBDebug.setter
    def getBDebug(self, BDebug: bool) -> None:
        self._BDebug = BDebug

    # Methods communication I/O
    def LineSend(self, Command: str) -> bool:
        """Write an ASCII command terminated with CR LF."""
        if not self.getComSerial.is_open:
            raise serial.SerialException("Serial port is not open.")
            return False

        if self.getComSerial.in_waiting:
            self.getComSerial.reset_input_buffer()

        FullCommand = f"{Command}\r\n".encode("ascii")
        self.getComSerial.write(FullCommand)

        if self.getBLogger():
            self.getLogger.Debug(Message=f"Sending command: {Command}")

        return True

    def LineRead(self) -> list[str]:
        """Read the expected number of response lines for the active protocol."""
        Lines = []

        if self.getProtocol == 1:
            MaxLines = 1
        elif self.getProtocol == 2:
            MaxLines = 5
        else:
            raise NotImplementedError(f"Error: Protocol {self.getProtocol} is not supported.")

        for _ in range(MaxLines):
            Line = self.getComSerial.readline().decode("ascii", errors="ignore").strip()
            if Line:
                Lines.append(Line)

        if self.getBLogger():
            self.getLogger.Debug(Message=f"Received lines: {Lines}")

        if Lines:
            self.setLastResponseTime()

        return Lines

    # Methods Protocol detection
    def getAutoProtocol(self) -> None:
        """Auto-detect protocol by sending a print command and inspecting the response."""
        if self.getProtocol:
            return

        # Send a print command to the scale to trigger a response.
        self.LineSend("S")

        # Read raw lines without protocol branching (can't use LineRead here).
        Lines = []
        for _ in range(5):
            Line = self.getComSerial.readline().decode("ascii", errors="ignore").strip()
            if Line:
                Lines.append(Line)

        if not Lines:
            raise RuntimeError("No response from scale during protocol detection.")

        MergedLines = " ".join(Lines)
        if re.search(r"[-+]?\s*[\d.]+\s*[a-zA-Z]+", Lines[0]):
            self.getProtocol = 1
            if self.getBLogger():
                self.getLogger.Info(Message="Bench scale: detected protocol 1 (single-line format)")

        elif any(h in MergedLines for h in ["GS", "No.", "Total"]):
            self.getProtocol = 2
            if self.getBLogger():
                self.getLogger.Info(Message="Bench scale: detected protocol 2 (multi-line GS/NT/GT format)")

        if self.getProtocol is None:
            raise RuntimeError(
                f"Could not detect scale protocol from output: {Lines}. "
                "Pass protocol=1 or protocol=2 explicitly."
            )

    def ParseLine(self, Line: str | list[str]) -> list[str] | list[list[str]] | None:
        """Extract a floating-point weight from a raw scale response line."""
        if isinstance(Line, list):
            Result = []
            for L in Line:
                ListLine = L.split()
                if ListLine:
                    Result.append(ListLine)
            return Result if Result else None
        elif isinstance(Line, str):
            ListLine = Line.split()
            return ListLine if ListLine else None
        else:
            raise TypeError("Line must be a string or list of strings.")

    # Methods Scale operations
    def getWeight(self) -> float | None:
        """Request the current weight and return it in the scale's native unit.

        Returns None if the scale does not return a parseable value.
        """
        self.LineSend("SI")

        time.sleep(self.getInterTimeCom)  # Wait briefly for the scale to respond

        Lines = self.LineRead()

        if not Lines:
            return None

        if self.getProtocol == 1:
            return self.ParseLine(Lines[0])
        elif self.getProtocol == 2:
            for Line in Lines:
                if Line.startswith(("GS", "NT", "GT")):
                    return self.ParseLine(Line)
        return None

    def Tare(self) -> bool:
        """Send the tare command, zeroing the display with the current load."""
        self.LineSend("T")

        time.sleep(self.getInterTimeCom)  # Wait briefly for the scale to respond

        Lines = self.LineRead()
        
        if Lines:
            LineList = self.ParseLine(Lines[0])
            
            if LineList[0:2] == ["T", "S"]:
                return True
            else:
                if self.getBLogger():
                    self.getLogger.Warning(Message=f"Tare command failed. Response: {Lines}")
                return False


    def setTare(self, Value: float) -> bool:
        """Preset a known tare value without placing a load on the pan.

        Args:
            value: Tare weight in the scale's native unit.
        """
        self.LineSend(f"TA {Value:.3f} g")

        time.sleep(self.getInterTimeCom)  # Wait briefly for the scale to respond

        Lines = self.LineRead()
        
        if Lines:
            LineList = self.ParseLine(Lines[0])
    
            if LineList[0:2] == ["TA", "A"]:
                if abs((float(LineList[2])-Value)/Value) < 0.01:
                    return True
                else:
                    if self.getBLogger():
                        self.getLogger.Warning(Message=f"setTare command failed. To large difference between requested and actual tare value. Requested: {Value}, Actual: {LineList[3]}")
                    return False
            else:
                if self.getBLogger():
                    self.getLogger.Warning(Message=f"setTare command failed. Response: {Lines}")
                return False

    def Zero(self) -> bool:
        """Send the zero command, resetting the scale's internal zero point."""
        self.LineSend("Z")

        time.sleep(self.getInterTimeCom)  # Wait briefly for the scale to respond

        Lines = self.LineRead()
        
        if Lines:
            LineList = self.ParseLine(Lines[0])
    
            if LineList == ["Z", "A"]:
                return True
            else:
                if self.getBLogger():
                    self.getLogger.Warning(Message=f"Zero command failed. Response: {Lines}")
                return False

    def Display(self, Message: str = "Hello") -> bool:
        """Send a message to the scale's display (if supported)."""
        self.LineSend(f'D "{Message}"')

        Lines = self.LineRead()
        
        if Lines:
            LineList = self.ParseLine(Lines[0])
    
            if LineList[0:2] == ["D", "A"]:
                return True
            else:
                if self.getBLogger():
                    self.getLogger.Warning(Message=f"Display command failed. Response: {Lines}")
                return False
        return True

    def DisplayWeight(self) -> bool:
        """Send a message to the scale's display (if supported)."""
        self.LineSend(f"DW")

        time.sleep(self.getInterTimeCom)  # Wait briefly for the scale to respond

        Lines = self.LineRead()
        
        if Lines:
            LineList = self.ParseLine(Lines[0])
    
            if LineList[0:2] == ["DW", "A"]:
                return True
            else:
                if self.getBLogger():
                    self.getLogger.Warning(Message=f"Display weight command failed. Response: {Lines}")
                return False
        return True

    def getBConnected(self) -> bool:
        """Return True if the serial port is open."""
        return self.getComSerial and self.getComSerial.is_open

    def getBResponsive(self) -> bool:
        """Return True if the scale replies to a print command within the timeout."""
        if self.getBConnected():    
            try:
                if self.DisplayWeight():
                    self.setLastResponseTime()
                    return True
            except serial.SerialException:
                pass

        return False

    def Close(self) -> None:
        """Close the serial port."""
        if self.getComSerial.is_open:
            self.getComSerial.close()

    def Disconnect(self) -> None:
        """Close the serial port."""
        self.Close()

class AutoReconSerialScale:
    """Wrapper around SerialScale that silently reconnects on serial errors.

    All method calls are forwarded to the underlying SerialScale. If the
    connection is lost, the wrapper reconnects before retrying the call.

    Args:
        *args: Positional arguments forwarded to SerialScale.
        retry_delay: Seconds to wait between reconnection attempts.
        **kwargs: Keyword arguments forwarded to SerialScale.
    """

    def __init__(self, *args, RetryDelay: float = 2.0, MaxDelay: float = 60, **kwargs):
        self._args = args
        self._kwargs = kwargs

        # Reconnection parameters
        self._RetryDelay = RetryDelay
        self._MaxDelay = MaxDelay

        # Scale manager
        self._SerialScale: SerialScale | None = None

        # Connection to the scale
        self.Connect()

    # Reconnection parameters
    @property
    def getRetryDelay(self) -> float:
        return self._RetryDelay

    @getRetryDelay.setter
    def getRetryDelay(self, RetryDelay: float) -> None:
        self._RetryDelay = RetryDelay

    @property
    def getMaxDelay(self) -> float:
        return self._MaxDelay

    @getMaxDelay.setter
    def getMaxDelay(self, MaxDelay: float) -> None:
        self._MaxDelay = MaxDelay

    # Scale manager
    @property
    def getSerialScale(self) -> SerialScale | None:
        return self._SerialScale

    @getSerialScale.setter
    def getSerialScale(self, SerialScale: SerialScale | None) -> None:
        self._SerialScale = SerialScale

    # Methods
    def Connect(self) -> None:
        """Block until a SerialScale connection is established."""
        while True:
            try:
                self.getSerialScale = SerialScale(*self._args, **self._kwargs)
                print("SerialScale connected.")
                return
            except SerialException as e:
                print(f"Serial connection failed: {e}. Retrying...")
                time.sleep(self._RetryDelay)

    def EnsureConnection(self) -> None:
        """Re-connect if the underlying scale is no longer connected."""
        if self.getSerialScale is None or not self.getSerialScale.getBConnected():
            print("Lost connection. Attempting reconnect...")
            self.Connect()

    def __getattr__(self, Name): #Vérifier cette partie du code et la comprendre et vérifier si pas mieux de mettre scale serial en parent.
        """Forward method calls to internal SerialScale, with reconnection if needed."""

        def method(*args, **kwargs):
            self.EnsureConnection()
            try:
                return getattr(self.getSerialScale, Name)(*args, **kwargs)
            except SerialException:
                print("Serial error during operation. Reconnecting...")
                self.Connect()
                return getattr(self.getSerialScale, Name)(*args, **kwargs)
        return method


class Scale:
    """High-level bench-scale driver.

    Construction is lightweight; call start() to open the port and infer protocol.
    """

    def __init__(self, Port: str, Baudrate: int = 9600, Timeout: float = 2.0, BAutoReconnect: bool = False,
                 Protocol: int | None = None, Logger: LogManager | None = None) -> None:
        """Store connection parameters without opening the port.

        Args:
            SerialPort: Serial device path, e.g. "/dev/ttyUSB0" or "COM3".
            Baudrate: Baud rate matching the scale's RS-232 setting.
            Timeout: Per-readline timeout in seconds passed to SerialScale.
            Protocol: Force protocol 1 or 2. Omit to auto-detect on start().
        """
        # Connection parameters
        self._SerialPort = Port
        self._Baudrate = Baudrate
        self._Timeout = Timeout
        self._BAutoReconnect = BAutoReconnect

        # Communication protocol (1, 2...) or None for auto-detection
        self._Protocol = Protocol

        # Scale manager
        self._Scale: SerialScale | AutoReconSerialScale | None = None

        # Test and debug
        self._Logger = Logger

    
    # Connection parameters
    @property
    def getSerialPort(self) -> str:
        return self._SerialPort

    @getSerialPort.setter
    def getSerialPort(self, Port: str) -> None:
        self._SerialPort = Port

    @property
    def getBaudrate(self) -> int:
        return self._Baudrate

    @getBaudrate.setter
    def getBaudrate(self, Baudrate: int) -> None:
        self._Baudrate = Baudrate

    @property
    def getTimeout(self) -> float:
        return self._Timeout

    @getTimeout.setter
    def getTimeout(self, Timeout: float) -> None:
        self._Timeout = Timeout

    @property
    def getBAutoReconnect(self) -> bool:
        return self._BAutoReconnect

    @getBAutoReconnect.setter
    def getBAutoReconnect(self, BAutoReconnect: bool) -> None:
        self._BAutoReconnect = BAutoReconnect

    # Communication protocol (1, 2...) or None for auto-detection
    @property
    def getProtocol(self) -> int | None:
        return self._Protocol

    @getProtocol.setter
    def getProtocol(self, Protocol: int | None) -> None:
        self._Protocol = Protocol

    # Scale manager
    @property
    def getScale(self) -> SerialScale | AutoReconSerialScale | None:
        return self._Scale

    @getScale.setter
    def getScale(self, Scale: SerialScale | AutoReconSerialScale | None) -> None:
        self._Scale = Scale

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

        if self.getScale is not None:
            self.getScale.getLogger = Logger

    @property
    def getBLogger(self) -> bool:
        return self._Logger is not None

    # Methods
    def Start(self, Timeout: float = 10.0) -> None:
        """Open the serial port, infer protocol, and verify the scale is responsive.

        Args:
            Timeout: Maximum seconds to wait for the scale to respond.
        Raises:
            TimeoutError: If the scale does not respond within "Timeout" seconds.
        """
        Deadline = time.time() + Timeout
        LastExc: Exception | None = None

        while time.time() < Deadline:
            if self.getScale is not None:
                self.getScale.Disconnect()
                self.getScale = None

            try:
                if self.getBAutoReconnect:
                    self.getScale = AutoReconSerialScale(
                        Port=self.getSerialPort,
                        Baudrate=self.getBaudrate,
                        Timeout=self.getTimeout,
                        Protocol=self.getProtocol)
                else:
                    self.getScale = SerialScale(
                        Port=self.getSerialPort,
                        Baudrate=self.getBaudrate,
                        Timeout=self.getTimeout,
                        Protocol=self.getProtocol)

                if self.getBConnected():
                    if self.getScale.getBLogger():
                        self.getScale.getLogger.Info(f"Bench scale on {self.getSerialPort} is connected and responsive.")
                    return

            except (SerialException, Exception) as Exc:
                LastExc = Exc

            time.sleep(0.2)

        raise TimeoutError(
            f"Bench scale on {self.getSerialPort} did not respond within {Timeout}s. "
            f"Last error: {LastExc}")

    def getWeight(self) -> float | None:
        """Return the current weight, or None if the scale returns no value."""
        if self.getScale is not None:
            return self.getScale.getWeight()
        return None

    def Tare(self) -> None:
        """Tare the scale and wait briefly for the display to settle."""
        if self.getScale is not None:
            self.getScale.Tare()
        else:
            raise RuntimeError("Scale is not connected; cannot tare.")

    def setTare(self, Value: float) -> None:
        """Preset a known tare value without placing a load on the pan.

        Args:
            value: Tare weight in the scale's native unit.
        """
        """Tare the scale and wait briefly for the display to settle."""
        if self.getScale is not None:
            self.getScale.setTare(Value=Value)
        else:
            raise RuntimeError("Scale is not connected; cannot tare.")

    def Zero(self) -> None:
        """
        Send the zero command, resetting the scale's internal zero point.
        """
        if self.getScale is not None:
            self.getScale.Zero()
        else:
            raise RuntimeError("Scale is not connected; cannot tare.")

    def getBConnected(self) -> bool:
        """Return True if the serial port is open."""
        return self.getScale is not None and self.getScale.getBConnected()

    def getBResponsive(self) -> bool:
        return self.getScale is not None and self.getScale.getBResponsive()

    def Disconnect(self) -> None:
        """Close the serial port and release the underlying SerialScale."""
        if self.getScale is not None:
            self.getScale.Close()
            self.getScale = None

    def __del__(self) -> None:
        self.Disconnect()


if __name__ == "__main__":
    scale = SerialScale(Port="COM3", Protocol=1)

    if scale.getBConnected():
        print("Scale is connected.")
        if scale.getBResponsive():
            print("Scale is responsive.")
            print("Current weight:", scale.getWeight())
        else:
            print("Scale is unresponsive.")
    else:
        print("Scale not connected.")

    scale.Close()

    scale = AutoReconSerialScale(Port="COM3", Protocol=1)

    if scale.getBConnected():
        print("Scale is connected.")
        if scale.getBResponsive():
            print("Scale is responsive.")
            print("Current weight:", scale.getWeight())
        else:
            print("Scale is unresponsive.")
    else:
        print("Scale not connected.")

    scale.Close()

    scale = Scale(Port="COM3", Protocol=1)

    scale.Start()

    if scale.getScale.getBConnected():
        print("Scale is connected.")
        if scale.getScale.getBResponsive():
            print("Scale is responsive.")
            print("Current weight:", scale.getWeight())
        else:
            print("Scale is unresponsive.")
    else:
        print("Scale not connected.")

    scale.Disconnect()
    # TJRS zero  à la première connection, puis ensuite on peut peser
