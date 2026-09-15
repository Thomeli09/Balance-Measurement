# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# General Plotting library
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import axes, colors, cm
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.cm import ScalarMappable
import numpy as np
from highlight_text import fig_text
import os

# Custom Lib
from DataManagementLib import LenData


"""
Base de donnée

Improvements:
    Should add a list of axes to the ParamPLT object to avoid having to call plt.gca() each time as an option.
"""


# Display parameters
class ParamPLT:
    def __init__(self, Colour, LineType, Marker, Linesize, Fontsize):
        """
        Ajouter le système de liste si différents éléments, pas que pour les légendes,...
        """
        # Plot
        self.Colour = Colour
        self.ColourMap = 'viridis'
        self.LineType = LineType
        self.LineSize = Linesize
        self.MarkerType = Marker
        self.MarkerSize = Linesize
        self.Alpha = 1  # Blending value, from 0 (transparent) to 1 (opaque)
        self.HatchType = ''

        # Text
        self.TitleSize = Fontsize
        self.FontSize = Fontsize
        self.TicksSize = Fontsize
        self.LegendsSize = Fontsize
        self.XLabel = None
        self.YLabel = None
        self.ZLabel = None
        self.Title = None
        self.LegendTitle = None
        self.Legends = []
        self.BLegends = True
        self.BLegendsInsideBox = True  # To put the legend inside the plot or not
        self.LegendsLoc = 0  # Location of the legend (0 = best, ...)
        self.ColourBarTitle = None

        # Scale
        self.Scale = 1
        self.XScaleType = 'linear'
        self.YScaleType = 'linear'
        self.ZScaleType = 'linear'
        self.BXAxisDate = False
        self.XAxisDateFormat = mdates.DateFormatter('%Y-%m-%d')
        self.BXAxisDateRotate = False
        self.GenericScaleType = 'linear'
        self.Scale3D = 1

        # Plot Format
        self.PltAspect = None

        # Grid
        self.GridAxis = 'both'
        self.GridColour = None
        self.GridLineType = None
        self.GridLineSize = 0.4
        self.GridAlpha = 1
        self.BBox = True # To add a box around the plot or not

        # Limits
        self.XLimit = []
        self.YLimit = []
        self.Zlimit = []

        # Link to Figure and Axes
        self.Figure = None  # Figure
        self.BAxes = False  
        self.LAxes = []  # List of axes if BAxes = True
        self.PlottedObject = []  # List of plotted objects to be able to modify them later if needed
        self.BMappable = False
        self.LMappable = []  # List of mappable if BMappable = True

    # Plot
    @property
    def getBoolColour(self):
        if not self.Colour:
            return False
        else:
            return True

    @property
    def getColour(self):
        if not self.Colour:
            return None
        else:
            if isinstance(self.Colour, list):
                return self.Colour.pop(0)
            else:
                return self.Colour

    @getColour.setter
    def getColour(self, Colour):
        if isinstance(Colour, list):
            if isinstance(self.Colour, list):
                self.Colour = self.Colour + Colour
            else:
                self.Colour = None
                self.Colour = Colour
        else:
            self.Colour = Colour

    def getColourFillList(self, ShadesNumber, FloatMin=0.0, FloatMax=1.0, B2ParamPLTColour=True):
        """
        Create a list of Colours based on a Colour map and a range of values.

        Args:
            ShadesNumber (int): Number of shades to generate.
            FloatMin (float): Minimum value of the range.
            FloatMax (float): Maximum value of the range.
            B2ParamPLTColour (bool): If True, transfer the Colour to the ParamPLT object. Else, return the list of Colours.
        """
        CMap = cm.get_cmap(self.getColourMap)
        ColourRange = np.linspace(FloatMin, FloatMax, ShadesNumber)
        ListColours = [CMap(Value) for Value in ColourRange]

        if B2ParamPLTColour:
            self.getColour = ListColours
        else:
            return ListColours

    def getColourFullList(self, BEmptying=False):
        if isinstance(self.Colour, list):
            Temp = self.Colour
            if BEmptying:
                self.Colour = None
            return Temp
        else:
            print("Warning: No list of Colours found.")
            return self.Colour

    @property
    def getColourMap(self):
        return self.ColourMap

    @getColourMap.setter
    def getColourMap(self, ValColourMap):
        ColourMapDict = {"Perceptually Uniform Sequential": (0, 4),  # Indices: 0-4
                         0: "viridis", 1: "plasma", 2: "inferno", 3: "magma", 4: "cividis",

                         "Sequential": (5, 22),  # Indices: 5-22
                         5: "Greys", 6: "Purples", 7: "Blues", 8: "Greens", 9: "Oranges", 10: "Reds",
                         11: "YlOrBr", 12: "YlOrRd", 13: "OrRd", 14: "PuRd", 15: "RdPu", 16: "BuPu",
                         17: "GnBu", 18: "PuBu", 19: "YlGnBu", 20: "PuBuGn", 21: "BuGn", 22: "YlGn",

                         "Diverging": (23, 34),  # Indices: 23-34
                         23: "PiYG", 24: "PRGn", 25: "BrBG", 26: "PuOr", 27: "RdGy", 28: "RdBu",
                         29: "RdYlBu", 30: "RdYlGn", 31: "Spectral", 32: "coolwarm", 33: "bwr", 34: "seismic",

                         "Cyclic": (35, 37),  # Indices: 35-37
                         35: "twilight", 36: "twilight_shifted", 37: "hsv",

                         "Qualitative": (38, 49),  # Indices: 38-49
                         38: "Pastel1", 39: "Pastel2", 40: "Paired", 41: "Accent", 42: "Dark2",
                         43: "Set1", 44: "Set2", 45: "Set3", 46: "tab10", 47: "tab20", 48: "tab20b", 49: "tab20c",

                         "Miscellaneous": (50, 66),  # Indices: 50-66
                         50: "flag", 51: "prism", 52: "ocean", 53: "gist_earth", 54: "terrain", 55: "gist_stern",
                         56: "gnuplot", 57: "gnuplot2", 58: "CMRmap", 59: "cubehelix", 60: "brg",
                         61: "gist_rainbow", 62: "rainbow", 63: "jet", 64: "turbo", 65: "nipy_spectral", 66: "gist_ncar",

                         "Sequential (Miscellaneous)": (67, 82),  # Indices: 67-82
                         67: "binary", 68: "gist_yarg", 69: "gist_gray", 70: "gray", 71: "bone", 72: "pink",
                         73: "spring", 74: "summer", 75: "autumn", 76: "winter", 77: "cool", 78: "Wistia",
                         79: "hot", 80: "afmhot", 81: "gist_heat", 82: "copper",

                         "Perceptually Uniform Sequential (Reversed)": (83, 87),  # Indices: 83-87
                         83: "viridis_r", 84: "plasma_r", 85: "inferno_r", 86: "magma_r", 87: "cividis_r",

                         "Sequential (Reversed)": (88, 105),  # Indices: 88-105
                         88: "Greys_r", 89: "Purples_r", 90: "Blues_r", 91: "Greens_r", 92: "Oranges_r", 93: "Reds_r",
                         94: "YlOrBr_r", 95: "YlOrRd_r", 96: "OrRd_r", 97: "PuRd_r", 98: "RdPu_r", 99: "BuPu_r",
                         100: "GnBu_r", 101: "PuBu_r", 102: "YlGnBu_r", 103: "PuBuGn_r", 104: "BuGn_r", 105: "YlGn_r",
                         
                         "Diverging (Reversed)": (106, 117),  # Indices: 106-117
                         106: "PiYG_r", 107: "PRGn_r", 108: "BrBG_r", 109: "PuOr_r", 110: "RdGy_r", 111: "RdBu_r",
                         112: "RdYlBu_r", 113: "RdYlGn_r", 114: "Spectral_r", 115: "coolwarm_r", 116: "bwr_r", 117: "seismic_r",

                         "Cyclic (Reversed)": (118, 120),  # Indices: 118-120
                         118: "twilight_r", 119: "twilight_shifted_r", 120: "hsv_r",

                         "Miscellaneous (Reversed)": (121, 137),  # Indices: 121-137
                         121: "flag_r", 122: "prism_r", 123: "ocean_r", 124: "gist_earth_r", 125: "terrain_r", 126: "gist_stern_r",
                         127: "gnuplot_r", 128: "gnuplot2_r", 129: "CMRmap_r", 130: "cubehelix_r", 131: "brg_r",
                         132: "gist_rainbow_r", 133: "rainbow_r", 134: "jet_r", 135: "turbo_r", 136: "nipy_spectral_r", 137: "gist_ncar_r",

                         "Sequential (Miscellaneous) (Reversed)": (138, 153),  # Indices: 138-153
                         138: "binary_r", 139: "gist_yarg_r", 140: "gist_gray_r", 141: "gray_r", 142: "bone_r", 143: "pink_r",
                         144: "spring_r", 145: "summer_r", 146: "autumn_r", 147: "winter_r", 148: "cool_r", 149: "Wistia_r",
                         150: "hot_r", 151: "afmhot_r", 152: "gist_heat_r", 153: "copper_r"}

        self.ColourMap = ColourMapDict.get(ValColourMap, 'viridis')

    @property
    def getLineType(self):
        # Determine line type based on LineType input
        LineTypeDict = {0: '-', 1: '--', 2: '-.', 3: ':', 4: 'None'}
        LineType = LineTypeDict.get(self.LineType, '-')
        return LineType

    @getLineType.setter
    def getLineType(self, LineType):
        self.LineType = LineType

    @property
    def getLineSize(self):
        return self.LineSize

    @getLineSize.setter
    def getLineSize(self, Linesize):
        self.LineSize = Linesize

    @property
    def getMarker(self):
        MarkerTypeDict = {0: '', 1: '.', 2: ',', 3: 'o', 4: 'v', 5: '^',
                          6: '<', 7: '>', 8: '1', 9: '2', 10: '3', 11: '4',
                          12: '8', 13: 's', 14: 'p', 15: 'P', 16: '*', 17: 'h',
                          18: 'H', 19: '+', 20: 'x', 21: 'X', 22: 'D', 23: 'd',
                          24: '|', 25: '_'}
        MarkerType = MarkerTypeDict.get(self.MarkerType, '')
        return MarkerType

    @getMarker.setter
    def getMarker(self, Marker):
        self.MarkerType = Marker

    @property
    def getMarkerSize(self):
        return self.MarkerSize

    @getMarkerSize.setter
    def getMarkerSize(self, MarkerSize):
        self.MarkerSize = MarkerSize

    @property
    def getAlpha(self):
        return self.Alpha

    @getAlpha.setter
    def getAlpha(self, Alpha):
        self.Alpha = Alpha

    @property
    def getHatch(self):
        """
        Property that retrieves and modifies the `HatchType` attribute.
        - If `HatchType` is empty (`None` or equivalent), it returns `None`.
        - If `HatchType` is a list, it removes and returns the first element of the list (FIFO behavior).
        - If `HatchType` is not a list, it simply returns the value of `HatchType`.
        """

        # Check if `HatchType` is empty or `None`
        if not self.HatchType:
            return None  # Return None if no value is present
        else:
            # If `HatchType` is a list, pop and return the first element
            if isinstance(self.HatchType, list):
                return self.HatchType.pop(0)  # Remove the first element and return it
            else:
                # If `HatchType` is not a list, return the value directly
                return self.HatchType

    @getHatch.setter
    def getHatch(self, HatchType):
        """
        Sets the `HatchType` property of the object based on the specified hatch type (`HatchType`).
        The hatch type is mapped to predefined patterns using a dictionary.
        This method can handle simple integers or complex structures such as nested lists.

        Args:
            HatchType (int, list, or other): The hatch type to configure.
                - If `HatchType` is an integer, it is directly mapped to a pattern using the dictionary (Result = 1 Hatch).
                - If `HatchType` is a flat list, each element is individually mapped to create a combined pattern (Result = 1 Hatch).
                - If `HatchType` is a nested list, each sub-list is individually mapped to create multiple patterns (Result = # of sub-lists Hatch).
        """

        # Dictionary mapping numeric values to hatch patterns
        HatchTypeDict = {
            0: '', 1: '/', 2: '\\', 3: '|', 4: '-', 5: '+',
            6: 'x', 7: 'o', 8: 'O', 9: '.', 10: '*'
        }

        # Variables to store the result
        Hatch = ''   # Combined pattern if HatchType is a flat list
        LHatch = []  # List of patterns if HatchType contains nested lists

        # Check if `HatchType` is a list
        if isinstance(HatchType, list):
            for Item in HatchType:
                if isinstance(Item, list):  # If an element is a nested list
                    LItem = Item
                    Hatch = ''  # Reset `Hatch` for each sub-list
                    for Val in LItem:
                        # Add the pattern corresponding to the value to `Hatch`
                        Hatch += HatchTypeDict.get(Val, '')  
                    LHatch.append(Hatch)  # Append the complete pattern of the sub-list to `LHatch`
                else:  # If the element is an integer or a simple value
                    Val = Item
                    Hatch += HatchTypeDict.get(Val, '')  # Add the pattern directly
        else:  # If `HatchType` is not a list
            Hatch = HatchTypeDict.get(HatchType, '')  # Retrieve the corresponding pattern

        # Assign the final value to `self.HatchType`
        if LHatch:  # If `LHatch` contains complex patterns
            self.HatchType = LHatch
        else:  # Otherwise, use the simple pattern
            self.HatchType = Hatch

    def getHatchFullList(self, BEmptying=True):
        """
        Property that retrieves the full list of hatch patterns if `HatchType` is a list.
        If `HatchType` is not a list, it displays a warning message and returns the current value of `HatchType`.

        Returns:
            list or other: If `HatchType` is a list, it returns the list of hatch patterns and resets `HatchType` to `None`.
                           If `HatchType` is not a list, it prints a warning message and returns the current value of `HatchType`.
        """
        # Check if `HatchType` is a list
        if isinstance(self.HatchType, list):
            Temp = self.HatchType  # Store the current list of hatch patterns in a temporary variable
            if BEmptying:
                self.HatchType = None  # Reset `HatchType` to `None`
            return Temp  # Return the stored list
        else:
            # Print a warning message if `HatchType` is not a list
            print("Warning: No list of hatch found.")
            return self.HatchType  # Return the current value of `HatchType`

    # Text
    @property
    def getTitleSize(self):
        return self.TitleSize

    @getTitleSize.setter
    def getTitleSize(self, TitleSize):
        self.TitleSize = TitleSize

    @property
    def getFontSize(self):
        return self.FontSize

    @getFontSize.setter
    def getFontSize(self, Fontsize):
        self.FontSize = Fontsize

    @property
    def getTicksSize(self):
        return self.TicksSize

    @getTicksSize.setter
    def getTicksSize(self, TicksSize):
        self.TicksSize = TicksSize

    @property
    def getLegendsSize(self):
        return self.LegendsSize

    @getLegendsSize.setter
    def getLegendsSize(self, LegendsSize):
        self.LegendsSize = LegendsSize

    @property
    def getTitle(self):
        return self.Title

    @getTitle.setter
    def getTitle(self, Title):
        self.Title = Title

    @property
    def getLegendTitle(self):
        return self.LegendTitle

    @getLegendTitle.setter
    def getLegendTitle(self, LegendTitle):
        self.LegendTitle = LegendTitle

    @property
    def getXLabel(self):
        return self.XLabel

    @getXLabel.setter
    def getXLabel(self, XLabel):
        self.XLabel = XLabel

    @property
    def getYLabel(self):
        return self.YLabel

    @getYLabel.setter
    def getYLabel(self, YLabel):
        self.YLabel = YLabel

    @property
    def getZLabel(self):
        return self.ZLabel

    @getZLabel.setter
    def getZLabel(self, ZLabel):
        self.ZLabel = ZLabel

    def getLabelTitle(self, Title, XLabel, YLabel, ZLabel=None):
        self.Title = Title
        self.XLabel = XLabel
        self.YLabel = YLabel
        self.ZLabel = ZLabel

    @property
    def getLegends(self):
        if not self.Legends:
            return None
        else:
            return self.Legends.pop(0)

    @getLegends.setter
    def getLegends(self, Legends):
        self.Legends = Legends

    def getLegendsFullList(self, BEmptying=True):
        # Check if `Legends` is a list
        if isinstance(self.Legends, list):
            Temp = self.Legends  # Store the current list of legend in a temporary variable
            if BEmptying:
                self.Legends = None  # Reset `Legends` to `None`
            return Temp  # Return the stored list
        else:
            # Print a warning message if `Legends` is not a list
            print("Warning: No list of legend found.")
            return self.Legends  # Return the current value of `Legends`
  
    @property
    def getBLegends(self):
        return self.BLegends

    @getBLegends.setter
    def getBLegends(self, Bool):
        self.BLegends = Bool

    @property
    def getBLegendsInsideBox(self):
        return self.BLegendsInsideBox

    @getBLegendsInsideBox.setter
    def getBLegendsInsideBox(self, Bool):
        self.BLegendsInsideBox = Bool

    @property
    def getLegendsLoc(self):
        return self.LegendsLoc

    @getLegendsLoc.setter
    def getLegendsLoc(self, Loc):
        # Dictionary mapping integer values to legend locations
        LegendLocDict = {0: 'best', 1: 'upper right', 2: 'upper left', 3: 'lower left', 4: 'lower right',
                         5: 'right', 6: 'center left', 7: 'center right', 8: 'lower center', 9: 'upper center',
                         10: 'center', 'best': 'best', 'upper right': 'upper right', 'upper left': 'upper left', 
                         'lower left': 'lower left', 'lower right': 'lower right', 'right': 'right', 
                         'center left': 'center left', 'center right': 'center right', 
                         'lower center': 'lower center', 'upper center': 'upper center', 'center': 'center'}
        self.LegendsLoc = LegendLocDict.get(Loc, 'best')

    @property
    def getColourBarTitle(self):
        return self.ColourBarTitle

    @getColourBarTitle.setter
    def getColourBarTitle(self, Title):
        self.ColourBarTitle = Title

    # Scale
    @property
    def getScale(self):
        return self.Scale

    @getScale.setter
    def getScale(self, scale):
        self.Scale = scale

    def ScaleVal2Name(self, Val):
        ScaleTypeDict = {0: 'linear', 1: 'log', 2: 'logit',
                         3: 'symlog', 4: 'function',
                         5: 'functionlog', 6: 'asinh',
                         7: 'mercator', 8: None}
        ScaleType = ScaleTypeDict.get(Val, 'linear')
        return ScaleType

    @property
    def getXScaleType(self):
        return self.XScaleType

    @getXScaleType.setter
    def getXScaleType(self, Val):
        self.XScaleType = self.ScaleVal2Name(Val)

    @property
    def getYScaleType(self):
        return self.YScaleType

    @getYScaleType.setter
    def getYScaleType(self, Val):
        self.YScaleType = self.ScaleVal2Name(Val)

    @property
    def getZScaleType(self):
        return self.ZScaleType

    @getZScaleType.setter
    def getZScaleType(self, Val):
        self.ZScaleType = self.ScaleVal2Name(Val)

    @property
    def getBXAxisDate(self):
        return self.BXAxisDate

    @getBXAxisDate.setter
    def getBXAxisDate(self, Bool):
        self.BXAxisDate = Bool

    @property
    def getXAxisDateFormat(self):
        return self.XAxisDateFormat

    @getXAxisDateFormat.setter
    def getXAxisDateFormat(self, DateFormat):
        self.XAxisDateFormat = mdates.DateFormatter(DateFormat)

    @property
    def getBXAxisDateRotate(self):
        return self.BXAxisDateRotate

    @getBXAxisDateRotate.setter
    def getBXAxisDateRotate(self, Bool):
        self.BXAxisDateRotate = Bool

    @property
    def getGenericScaleType(self):
        return self.GenericScaleType

    @getGenericScaleType.setter
    def getGenericScaleType(self, Val):
        self.GenericScaleType = self.ScaleVal2Name(Val)

    @property
    def getScale3D(self):
        return self.Scale3D

    @getScale3D.setter
    def getScale3D(self, scale3D):
        self.Scale3D = scale3D

    @property
    def getFMT(self):
        # Construct plot format
        fmt = f"{self.getMarker}{self.getLineSize}{self.getColour}"
        return fmt

    # Plot Format
    @property
    def getAspect(self):
        return self.PltAspect

    @getAspect.setter
    def getAspect(self, Aspect):
        self.PltAspect = Aspect

    # Grid
    @property
    def getGridAxis(self):
        return self.GridAxis

    @getGridAxis.setter
    def getGridAxis(self, GridAxis):
        self.GridAxis = GridAxis

    @property
    def getGridColour(self):
        return self.GridColour

    @getGridColour.setter
    def getGridColour(self, Colour):
        self.GridColour = Colour

    def getGrid(self, Axis, Colour=None):
        if Axis == 1:
            self.getGridAxis = 'x'
        elif Axis == 2:
            self.getGridAxis = 'y'
        elif Axis >= 0:
            self.getGridAxis = 'both'
        else:
            self.getGridAxis = None

        self.getGridColour = Colour

        self.getGridLineType = None
        self.getGridLineSize = 0.4

    @property
    def getGridLineType(self):
        # Determine line type based on LineType input
        LineTypeDict = {0: '-', 1: '-', 2: '--', 3: '-.', 4: ':'}
        LineType = LineTypeDict.get(self.GridLineType, '-')
        return LineType

    @getGridLineType.setter
    def getGridLineType(self, LineType):
        self.GridLineType = LineType

    @property
    def getGridLineSize(self):
        return self.GridLineSize

    @getGridLineSize.setter
    def getGridLineSize(self, LineSize):
        self.GridLineSize = LineSize

    @property
    def getGridAlpha(self):
        return self.GridAlpha

    @getGridAlpha.setter
    def getGridAlpha(self, Val):
        self.GridAlpha = Val

    @property
    def getBBox(self):
        return self.BBox

    @getBBox.setter
    def getBBox(self, Bool):
        self.BBox = Bool

    # Limits
    @property
    def getXLimit(self):
        if not self.XLimit:
            return None
        else:
            return self.XLimit.pop(0)

    @getXLimit.setter
    def getXLimit(self, Limit):
        self.XLimit.append(Limit)
    
    @property
    def getYLimit(self):
        if not self.YLimit:
            return None
        else:
            return self.YLimit.pop(0)

    @getYLimit.setter
    def getYLimit(self, Limit):
        self.YLimit.append(Limit)
    
    @property
    def getZLimit(self):
        if not self.ZLimit:
            return None
        else:
            return self.ZLimit.pop(0)

    @getZLimit.setter
    def getZLimit(self, Limit):
        self.ZLimit.append(Limit)

    @property
    def getBoolXLimit(self):
        return bool(self.XLimit)
    
    @property
    def getBoolYLimit(self):
        return bool(self.YLimit)
    
    @property
    def getBoolZLimit(self):
        return bool(self.ZLimit)

    # Link to Figure and Axes
    @property
    def getFigure(self):
        return self.Figure

    @getFigure.setter
    def getFigure(self, Figure):
        self.Figure = Figure

    @property
    def getBAxes(self):
        return self.BAxes

    @getBAxes.setter
    def getBAxes(self, Bool):
        self.BAxes = Bool

    @property
    def getAxes(self):
        if not self.getBAxes:
            return None
        else:
            return self.LAxes

    @getAxes.setter
    def getAxes(self, Ax):
        Axes2Add = []

        # Case 1: Single Axes
        if isinstance(Ax, Axes):
            Axes2Add = [Ax]

        # Case 2: List / tuple / np.ndarray of Axes
        elif isinstance(Ax, (list, tuple, np.ndarray)):
            # If it's a numpy array, flatten it
            if isinstance(Ax, np.ndarray):
                Ax = Ax.flatten()
            # Collect valid Axes
            Axes2Add = [a for a in Ax if isinstance(a, Axes)]
            if not Axes2Add:
                print("Error: No valid Axes found in the provided collection.")
                return

        # Case 3: Not valid
        else:
            print("Error: The provided Ax is not a valid Axes or collection of Axes.")
            return

        # Store
        if self.getBAxes:
            self.LAxes.extend(Axes2Add)
        else:
            self.LAxes = Axes2Add
            self.getBAxes = True

    @property
    def getLastAx(self):
        if not self.getBAxes:
            print("Warning: No axes found.")
            return None
        else:
            return self.getAxes[-1]

    @property
    def getPlottedObject(self):
        if not self.PlottedObject:
            return None
        else:
            return self.PlottedObject

    @getPlottedObject.setter
    def getPlottedObject(self, PlottedObject):
        if isinstance(PlottedObject, list):
            self.PlottedObject.extend(PlottedObject)
        else:
            self.PlottedObject.append(PlottedObject)

    @property
    def getPlottedObjectNum(self):
        return len(self.getPlottedObject)

    def getPlottedObjectFromIndex(self, Index):
        return self.getPlottedObject[Index]

    @property
    def getBMappable(self):
        return self.BMappable

    @getBMappable.setter
    def getBMappable(self, Bool):
        self.BMappable = Bool

    @property
    def getMappable(self):
        if not self.getBMappable:
            return None
        else:
            return self.LMappable

    @getMappable.setter
    def getMappable(self, Mappable):
        # Verify if Mappable is an instance of Axes
        if not isinstance(Mappable, ScalarMappable):
            print("Error: The provided Mappable is not a valid mappable object.")
            return
        if not self.getBMappable:
            self.LMappable = [Mappable]
            self.getBMappable = True
        else:
            self.LMappable.append(Mappable)

    @property
    def getLastMappable(self):
        if not self.getBMappable:
            print("Warning: No mappable found.")
            return None
        else:
            return self.LMappable[-1]

"""
Fcts générales
"""
def ClosePlot(PlotOBJ=None):
    if PlotOBJ is None:
        plt.close()
    else:
        plt.close(PlotOBJ)

def CloseAllPlots():
    plt.close('all')

def ClosePlotsOnDemand():
    # To close all plots on demand
    input("Press Enter to close all plots...") 
    plt.close('all')

def StartPlots(paramPLT=None, Rows=1, Cols=1):
    """
    Start a new plot and link it to the ParamPLT object if provided.
    """
    Fig, Ax = plt.subplots(nrows=Rows, ncols=Cols)
    if paramPLT is not None:
        paramPLT.getFigure = Fig
        paramPLT.getAxes = Ax

def PLTSetWindowSize(Width, Height):
    """
    Set the size of the plot window.
    Args:
    - Width: Width of the window in inches.
    - Height: Height of the window in inches.
    """
    plt.gcf().set_size_inches(Width, Height)

def PLTLatexStyle():
    """
    Set the style of the plot to use LaTeX for text rendering. But is slower.
    """
    plt.rcParams['text.usetex'] = True

def PLTTitleAxis(paramPLT):
    """
    Add a title to the plot and label the axes based on the specified parameters.
    """
    plt.xlabel(paramPLT.getXLabel, fontsize=paramPLT.getFontSize)
    plt.ylabel(paramPLT.getYLabel, fontsize=paramPLT.getFontSize)
    plt.title(paramPLT.getTitle, fontsize=paramPLT.getTitleSize)

def PLTTitleModified(paramPLT, X=0.5, Y=0.95):
    """
    Allows to have a different title style than the default one.

    Args:
    - TitleText: Text of the title with the desired style. 
        Example: 'Text with <highlighted Colour::{"Colour": "red", "fontstyle": "italic", "fontweight": "bold"}>'
    - paramPLT: Object containing plot parameters.
    - X: X position of the title.
    - Y: Y position of the title.

    Improvements:
    - Add highlight_textprops to modify the style of the title without adding that in the TitleText.
    """
    fig_text(s=paramPLT.getTitle, x=X, y=Y, 
             fontsize=paramPLT.getTitleSize, color='black', 
             ha='center', va='center')

def PLTSizeAxis(paramPLT):
    """
    Set the size of the ticks on the plot.
    """
    plt.xticks(fontsize=paramPLT.getTicksSize)
    plt.yticks(fontsize=paramPLT.getTicksSize)

def PLTLegend(paramPLT):
    """
    Add a legend to the plot based on the specified parameters.

    Args:
    - paramPLT: Object containing plot parameters.
    """
    if paramPLT.getBLegends:
        if paramPLT.getBLegendsInsideBox:
            plt.legend(title=paramPLT.getLegendTitle, title_fontproperties={'size':paramPLT.getLegendsSize*1.2,'weight': 'bold'},
                       fontsize=paramPLT.getLegendsSize, loc=paramPLT.getLegendsLoc)
        else:
            plt.legend(title=paramPLT.getLegendTitle, title_fontproperties={'size':paramPLT.getLegendsSize*1.2,'weight': 'bold'},
                       fontsize=paramPLT.getLegendsSize, bbox_to_anchor=(1, 1), loc='upper left')

def UpdatePlotColoursAndLegend(LColours):
    """
    Update the Colours of the lines in the plot based on a list of Colours.

    Args:
    - LColours: List of Colours to apply to the lines in the plot.
    """
    # Get the current axis
    ax = plt.gca()
    
    # Verify that the number of Colours matches the number of lines
    if len(LColours) != len(ax.lines):
        print("Error: The number of Colours does not match the number of lines.")
        return
    
    # Update the Colours of the lines
    for Line, Colour in zip(ax.lines, LColours):
        Line.set_color(Colour)

    # Update the legend
    plt.legend()
    # plt.draw()  # Redraws the figure (updates existing)
    plt.show()

def PLTLegendWithTitlesSubtitles(LegendTitle, LLegendSubtitles, LSubtitlesPositions, paramPLT, TitleSizeRatio=1.1, SubtitlesSizeRatio=1.0, ax=None):
    """
    Add a legend with a main title and multiple subtitles at specified positions.

    Args:
        LegendTitle: Main title of the legend.
        LLegendSubtitles: List of subtitles to be added to the legend.
        LSubtitlesPositions: List of positions for the subtitles in the legend.
        paramPLT: Object containing plot parameters.
        TitleSizeRatio: Ratio to adjust the size of the main title.
        SubtitlesSizeRatio: Ratio to adjust the size of the subtitles.
        ax: Axis object to which the legend will be added. If None, the current axis will be used.

    Returns:

    Note: 
    -The subtitles are added as empty lines with the specified text, that can lead to some issues.
    -This function should be used after PLTShow() or PLTMultiPlot() to work properly.

    Improvements:
    - Refine the position of the subtitles based on the number of labels in the legend.
    - Add an argument to specify the Colour of the subtitles.
    """
    # Get the current axis if not provided
    if ax is None:
        print("Info: No axis provided, the current axis is used.")
        ax = plt.gca()

    # Get the current legend handles and labels
    handles, labels = ax.get_legend_handles_labels()

    # Adding the subtitles to the legend
    for Subtitle, Position in zip(LLegendSubtitles, LSubtitlesPositions):
        if 0 <= Position <= len(handles):  # Prevent IndexError
            handles.insert(Position, plt.Line2D([], [], color='none', label=Subtitle))

    # Adding the main title to the legend
    if paramPLT.getBLegendsInsideBox:
        Legend = ax.legend(handles=handles,title=LegendTitle, fontsize=paramPLT.getTitleSize, 
                           loc=paramPLT.getLegendsLoc)
    else:
        Legend = ax.legend(handles=handles,title=LegendTitle, fontsize=paramPLT.getTitleSize,
                           bbox_to_anchor=(1, 1), loc='upper left')

    # Setting the title properties
    FormatText(Text=Legend.get_title(), Fontsize=paramPLT.getLegendsSize * TitleSizeRatio, Weight=None,
               Style=None, Family=None, Colour=None, BackgroundColour=None, Alpha=None)

    # Setting the subtitles properties
    for text in Legend.get_texts():
        if text.get_text() in LLegendSubtitles: # In case of the subtitles
            FormatText(Text=text, Fontsize=paramPLT.getLegendsSize * SubtitlesSizeRatio, Weight='bold',
                       Style=None, Family=None, Colour=None, BackgroundColour=None, Alpha=None)
        else:  # In case of the different labels
            pass

def PLTColourBar(paramPLT, Location=0, Fraction=0.10, Padding=-1, Spacing=0, BDrawEdges=False):
    """
    Add a Colour bar to the plot based on the specified parameters.

    Args:
    - paramPLT: Object containing plot parameters.
    - Location: Location of the Colour bar (0: right, 1: left, 2: top, 3: bottom).
    - Fraction: Fraction of the original axes to use for the Colour bar.
    - Padding: Padding between the Colour bar and the plot. If negative, a default value is used based on the location.
    - Spacing: Uniformity of the Colour bar (0: uniform, 1: proportional).
    - BDrawEdges: Boolean indicating whether to draw edges around the Colour bar.
    """
    Fig = paramPLT.getFigure
    if Fig is None:
        print("Warning: No figure found for the Colour bar.")
        return
    Mappable = paramPLT.getLastMappable
    if Mappable is None:
        print("Warning: No mappable found for the Colour bar.")
        return
    Ax = paramPLT.getLastAx
    if Ax is None:
        print("Warning: No axis found for the Colour bar.")
        return
    # Location of the Colour bar
    LocationDict = {0: 'right', 1: 'left', 2: 'top', 3: 'bottom'}
    Location = LocationDict.get(Location, 'right')

    # Padding between the Colour bar and the plot
    if Padding<0:
        PaddingDict = {'right': 0.05, 'left': 0.05, 'top': 0.15, 'bottom': 0.15}
        Padding = PaddingDict.get(Location, 0.05)
    else:
        Padding = Padding

    # Uniformity of the Colour bar
    SpacingDict = {0: 'uniform', 1: 'proportional'}
    Spacing = SpacingDict.get(Spacing, 'uniform')

    Cb = Fig.Colourbar(mappable=Mappable, ax=Ax, location=Location, fraction=Fraction, pad=Padding, 
                      format=None, spacing=Spacing, drawedges=BDrawEdges)
    Cb.set_label(label=paramPLT.getColourBarTitle, size=paramPLT.getFontSize)
    Cb.ax.tick_params(labelsize=paramPLT.getTicksSize)

def PLTGrid(paramPLT):
    if paramPLT.getGridAxis:
        plt.grid(axis=paramPLT.getGridAxis,
                 color=paramPLT.getColour,
                 linestyle=paramPLT.getGridLineType,
                 linewidth=paramPLT.getGridLineSize,
                 alpha=paramPLT.getGridAlpha)

def PLTLimit(paramPLT):
    if paramPLT.getBoolXLimit:
        plt.xlim(paramPLT.getXLimit)
    if paramPLT.getBoolYLimit:
        plt.ylim(paramPLT.getYLimit)

def PLTCmptLimit(Variable, Ratio=0.1):
    """
    Compute the limits of the plot based on the variable and a ratio.

    Improvements:
    - Based the computation on the current registered limits (self.XLimit, self.YLimit, self.ZLimit).
    """
    # Verify if the variable is empty
    if LenData(Variable) <= 0:
        print("Warning: The variable is empty, no plotting range will be set.")
        # Return None for both limits
        return [None, None] 
    
    else:
        MaxVal = max(Variable)
        MinVal = min(Variable)
        Delta = MaxVal-MinVal
        LowerLimit = MinVal-Delta*Ratio
        UpperLimit = MaxVal+Delta*Ratio
        return [LowerLimit, UpperLimit]

def PLTScaleType(paramPLT):
    """

    """
    if paramPLT.getXScaleType:
        plt.xscale(paramPLT.getXScaleType)
    if paramPLT.getYScaleType:
        plt.yscale(paramPLT.getYScaleType)

def PLTDate(paramPLT):
    """
    Format the x-axis to display dates properly.
    """
    if paramPLT.getBXAxisDate:
        plt.gca().xaxis.set_major_formatter(paramPLT.getXAxisDateFormat)

        if paramPLT.getBXAxisDateRotate:
            plt.gcf().autofmt_xdate() # Rotate labels

def PLTBox(paramPLT):
    """
    Remove or add the box around the plot based on the specified parameter.
    """
    plt.box(on=paramPLT.getBBox)

def PLTShow(paramPLT, BMultiplot=False):
    PLTTitleAxis(paramPLT)

    PLTSizeAxis(paramPLT)

    if paramPLT.getAspect:
        plt.gca().set_aspect('equal', adjustable='box')

    PLTLegend(paramPLT)

    PLTGrid(paramPLT)

    PLTLimit(paramPLT)

    PLTScaleType(paramPLT)

    PLTDate(paramPLT)

    PLTBox(paramPLT)

    if not BMultiplot:
        plt.show(block=False)  # Show plot without blocking

def PLTMultiPlot(paramPLT, Rows, Cols=1, Index=1, BStartPLT=True, BAvoidOverlapping=True, BCurrPLTax=False):
    """
    Allows to create a grid of subplots in a single figure.

    Args:
        paramPLT (ParamPLT): ParamPLT object containing plot parameters.
        Rows (int): Number of rows for the subplot grid.
        Cols (int): Number of columns for the subplot grid.
        Index (int): Current index for the subplot.
        BStartPLT (bool): Flag to indicate whether to start a new plot.
        BAvoidOverlapping (bool): Flag to avoid overlapping of labels, plots, etc.
        BCurrPLTax (bool): Flag to indicate whether the function returns the current axis object or not.

    Warning:
        The title of the plot should be set before calling this function, otherwise it will set the subtitle.
        BAvoidOverlapping may need to be set to False in some cases when filling the plot does not work as intended.

    Returns :
        Index: Updated index for the next subplot.
        AxesSubplot or None: Current axis object if BCurrPLTax is True; otherwise not returned.

    Improvements:
        Ability to resize the figure to fit all subplots and take into account the legend size.
    """
    if Index == 1:
        if BStartPLT:  # To start a new plot or not
            StartPlots(paramPLT=paramPLT, Rows=Rows, Cols=Cols)
        ax = plt.subplot(Rows, Cols, Index)
        plt.suptitle(paramPLT.getTitle, fontsize=paramPLT.getTitleSize, fontweight='bold') # Set the main title of the plot
    elif Index == Rows * Cols + 1:
        if BAvoidOverlapping:
            plt.tight_layout() # Avoid overlapping of labels, plots, etc.
        PLTShow(paramPLT)
        ax = None
    elif 1 < Index <= Rows * Cols:
        PLTShow(paramPLT, BMultiplot=True)
        ax = plt.subplot(Rows, Cols, Index)
    else:
        print("Warning: Invalid index for subplot.")
        ax = None

    Index += 1  # Increment the index for the next subplot

    # Return the current index and None if the index is invalid and the current axis object
    if BCurrPLTax:
        return Index, ax
    else:
        return Index

def PLTUpdateLayout():
    plt.tight_layout()

def PLTScreenMaximize(BTaskbar=True, BUpdateLayout=True, PLTTimePause=0.1):
    if BTaskbar:
        plt.get_current_fig_manager().window.state('zoomed')
    else:
        plt.get_current_fig_manager().full_screen_toggle()

    if BUpdateLayout:
        plt.pause(PLTTimePause) # Pause to allow the window to maximize and UpdateLayout to work
        # in case of unreliable behavior, increase the pause duration
        PLTUpdateLayout()

def PLTScreenSize(Width_cm, Height_cm, Scale=1, BUpdateLayout=True, PLTTimePause=0.1):
    """
    Set the size of the plot window in centimeters.

    Args:
        Width_cm (float): Width of the plot window in centimeters.
        Height_cm (float): Height of the plot window in centimeters.
        Scale (float): Optional scaling of width/height.
        BUpdateLayout (bool): Flag to update the layout after resizing.
        PLTTimePause (float): Time to pause for layout update.

    """
    # Convert centimeters to inches (1 inch = 2.54 cm)
    Width_in = (Width_cm / 2.54) * Scale
    Height_in = (Height_cm / 2.54) * Scale

    # Set the figure size in inches
    fig = plt.gcf()  # Get current figure
    fig.set_size_inches(Width_in, Height_in)

    if BUpdateLayout:
        plt.pause(PLTTimePause) # Pause to allow the window to maximize and UpdateLayout to work
        # in case of unreliable behavior, increase the pause duration
        PLTUpdateLayout()

def PLTSave(FileName, Width_cm, Height_cm, Scale=1, DPI=300, Format=1, BUpdateLayout=True, PLTTimePause=0.1, BCreateDir=False ,BClose=False):
    """
    Save the current plot to a file with customizable options.
    Args:
        FileName (str): Output filename (extension optional).
        Width_cm (float): Width of the figure in centimeters.
        Height_cm (float): Height of the figure in centimeters.
        Scale (float): Scale factor to apply to width and height.
        DPI (int): Dots per inch (resolution).
        Format (str or int): Format type (e.g., "png", 1, "pdf", etc.).
        BUpdateLayout (bool): Flag to update the layout after resizing.
        PLTTimePause (float): Time to pause for layout update.
        BCreateDir (bool): Flag to create the directory if it doesn't exist.
        BClose (bool): Whether to close the figure after saving.
    Returns:
        None: This function does not return anything.
    """

    # Ensure the directory exists
    directory = os.path.dirname(FileName) # Get the directory from the filename
    if directory and not os.path.exists(directory): # Check if there needs a directory and if it exists
        if BCreateDir: # Create the directory if it doesn't exist
            print(f"Info : Creating directory: {directory}")
            os.makedirs(directory)
        else:
            print(f"Warning : Directory <<{directory}>> does not exist. File will not be saved.")
            return
    
    # Dictionary to map format values to file extensions
    FormatDict = {'png': '.png', 1: '.png', 'pdf': '.pdf', 2: '.pdf', 
                  'svg': '.svg', 3: '.svg', 'eps': '.eps', 4: '.eps', 
                  'jpg': '.jpg', 5: '.jpg', 'jpeg': '.jpeg', 6: '.jpeg'}
    FormatName = FormatDict.get(Format, 'png')  # Default to PNG if format is not recognized

    FullName = FileName + FormatName

    # Set the figure size in inches
    PLTScreenSize(Width_cm=Width_cm, Height_cm=Height_cm, Scale=Scale, BUpdateLayout=BUpdateLayout, PLTTimePause=PLTTimePause)

    # Get the current figure
    fig = plt.gcf()

    # Save the plot to a file
    try:
        fig.savefig(fname=FullName, dpi=DPI, bbox_inches='tight')
        print(f"Info : Plot saved as {FullName}")
    except :
        print(f"Warning : Failed to save the plot as {FullName}. Check the file path and permissions.")

    if BClose:
        plt.close()

def PLTShowRefSavePlace():
    """
    Show the path where the plots are saved.
    """
    print("Info : The reference path for saving plots is:")
    print("Info : ", os.getcwd())

def DefaultParamPLT():
    return ParamPLT(Colour='black', LineType=0, Marker=0, Linesize=2, Fontsize=16)

# Version in 3D case with PLT3DShow

"""
Type de Plots
"""
# 2D


def PLTText(XY, Text, paramPLT, FontFamily=0, FontStyle=0, FontWeight=0, HAlignement=0, Rotation=-1, RotationMode=0, BAbsoluteCoord=True):
    """
    Adds text to a plot at specified coordinates with customizable parameters.

    Args:
        XY (tuple): Coordinates (x, y) where the text will be placed.
        Text (str): The text to be displayed on the plot.
        paramPLT (object): Object containing plot parameters.
        FontFamily (int): Integer value representing the font family.
        FontStyle (int): Integer value representing the font style.
        FontWeight (int): Integer value representing the font weight.
        HAlignement (int): Integer value representing the horizontal alignment of the text.
        Rotation (int or float): Angle of rotation for the text.
        RotationMode (int): Mode of rotation (0 for default, 1 for anchor).
        BAbsoluteCoord (bool): If True, the coordinates are in absolute terms; if False, they are relative to the axes.

    Returns:
        None: This function does not return anything. It simply adds text to the plot.
    """
    # Dictionary mapping integer values to font families
    TextFontDict = {0: 'sans-serif', 1: 'serif', 2: 'cursive', 3: 'fantasy', 4: 'monospace'}
    FontFamily = TextFontDict.get(FontFamily, 'sans-serif')

    # Dictionary mapping integer values to fontstyles
    TextFontStyleDict = {0: 'normal', 1: 'italic', 2: 'oblique'}
    FontStyle = TextFontStyleDict.get(FontStyle, 'normal')

    # Dictionary mapping integer values to font weights
    TextFontWeightDict = {0: 'normal', 1: 'ultralight', 2: 'light', 3: 'regular', 4: 'book', 5: 'medium', 6: 'roman',
                      7: 'semibold', 8: 'demibold', 9: 'bold', 10: 'heavy', 11: 'extra bold', 12: 'black'}
    FontWeight = TextFontWeightDict.get(FontWeight, 'normal')

    # Dictionary mapping integer values to horizontal alignment
    TextHAlignementDict = {0: 'center', 1: 'left', 2: 'right'}
    HAlignement = TextHAlignementDict.get(HAlignement, 'center')

    # Dictionary mapping integer values to rotation
    TextRotationDict = {-1: 'horizontal', -2: 'vertical'}
    Rotation = TextRotationDict.get(Rotation, Rotation)

    # Dictionary mapping integer values to rotation mode
    TextRotationModeDict = {0: 'default', 1: 'anchor'}
    RotationMode = TextRotationModeDict.get(RotationMode, 'default')

    # Position in absolute coordinates or relative to the axes
    CoordType = None
    if not BAbsoluteCoord:
        ax = plt.gca()
        CoordType = ax.transAxes

    # Based on stored Ax or on Ax from plt.gca()
    if paramPLT.getBAxes:
        Ax = paramPLT.getLastAx
    else:
        Ax = plt.gca()
       
    if Ax is not None:
        Ax.text(x=XY[0], y=XY[1], s=Text,
                color=paramPLT.getColour, alpha=paramPLT.getAlpha,
                fontfamily=FontFamily, fontstyle=FontStyle, fontweight=FontWeight, fontsize=paramPLT.getTicksSize,
                horizontalalignment=HAlignement, rotation=Rotation, rotation_mode=RotationMode, bbox=dict(facecolor='white', alpha=0.5, edgecolor='k'))
        # transform=CoordType

def PLTPlot(XValues, YValues, paramPLT):
    """
    Creates a 2D plot using customizable parameters.

    Args:
        XValues (list ou array-like): X-axis values for the plot.
        YValues (list ou array-like): Y-axis values for the plot.
        paramPLT (objet): Object containing plot parameters.

    Returns:
        None: This function does not return anything. It simply displays the plot.
    """
    ln = plt.plot(XValues, YValues,
                  color=paramPLT.getColour,
                  alpha=paramPLT.getAlpha,
                  linestyle=paramPLT.getLineType,
                  linewidth=paramPLT.getLineSize,
                  marker=paramPLT.getMarker,
                  markersize=paramPLT.getMarkerSize,
                  label=paramPLT.getLegends)

    paramPLT.getPlottedObject = ln[0]  # Store the line object for later use

def PLTEmptyPlot(paramPLT):
    """
    Creates an empty plot with customizable parameters.
    Args:
        paramPLT (object): Object containing plot parameters.
    Returns:
        None: This function does not return anything. It simply displays the empty plot.
    """
    PLTPlot(XValues=[], YValues=[], paramPLT=paramPLT)

def PLTUpdatePlot(XValues, YValues, paramPLT, index):
    """
    Updates an existing plot with new X and Y values.
    Args:
    - XValues (list or array-like): New X-axis values for the plot.
    - YValues (list or array-like): New Y-axis values for the plot.
    - paramPLT (object): Object containing plot parameters.
    - index (int): Index of the line to update in the current axis.
    Returns:
    None: This function does not return anything. It simply updates the existing plot with new data.
    """
    Line = paramPLT.getPlottedObjectFromIndex(index)
    if isinstance(Line, Line2D):
        Line.set_data(XValues, YValues)
    else:
        print(f"Warning: The object at index {index} is not a Line2D object and cannot be updated.")

def PLTPlotSeries(LXValues, LYValues, paramPLT):
    """
    Creates a 2D plot with multiple curves from lists of X and Y values.

    Args:
        LXValues (list of lists or array-like): List of X-axis values for each curve.
        LYValues (list of lists or array-like): List of Y-axis values for each curve.
        paramPLT (object): Object containing plot parameters.

    Returns:
        None: This function does not return anything. It simply displays the plot.
    """

    for XValues, YValues in zip(LXValues, LYValues):
        PLTPlot(XValues, YValues, paramPLT)


def PLTVHLine(Val, paramPLT, BRelative=True, SecValMin=0, SecValMax=1, BOrientation=True):
    """
    Plots a vertical or horizontal line on the plot, based on the specified parameters.

    Args:
    - Val (float): Value at which to draw the line (x-coordinate for vertical line, y-coordinate for horizontal line),
        but allows Array-like input to draw multiple lines only if BRelative is False.
    - paramPLT (object): Object containing plot parameters.
    - BRelative (bool): Boolean flag to specify if the secondary axis values are in relative units (0 to 1) or absolute units.
    - SecValMin (float): Minimum value for the secondary axis (y-axis for vertical line, x-axis for horizontal line) 
        and is in relative units (0 to 1) or absolute units based on BRelative.
    - SecValMax (float): Maximum value for the secondary axis (y-axis for vertical line, x-axis for horizontal line) 
        and is in relative units (0 to 1) or absolute units based on BRelative.
    - BOrientation (bool): Boolean flag to specify the orientation of the line.
    """
    if BOrientation:  # Vertical line
        if BRelative:
            plt.axvline(x=Val, ymin=SecValMin, ymax=SecValMax,
                        color=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize,
                        marker=paramPLT.getMarker, markersize=paramPLT.getMarkerSize, 
                        alpha=paramPLT.getAlpha, label=paramPLT.getLegends)
        else:
            plt.vlines(x=Val, ymin=SecValMin, ymax=SecValMax,
                       color=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize,
                       marker=paramPLT.getMarker, markersize=paramPLT.getMarkerSize, 
                       alpha=paramPLT.getAlpha, label=paramPLT.getLegends)
    elif BOrientation == False:  # Horizontal line
        if BRelative:
            plt.axhline(y=Val, xmin=SecValMin, xmax=SecValMax,
                        color=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize,
                        marker=paramPLT.getMarker, markersize=paramPLT.getMarkerSize, 
                        alpha=paramPLT.getAlpha, label=paramPLT.getLegends)
        else:
            plt.hlines(y=Val, xmin=SecValMin, xmax=SecValMax,
                       color=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize,
                       marker=paramPLT.getMarker, markersize=paramPLT.getMarkerSize, 
                       alpha=paramPLT.getAlpha, label=paramPLT.getLegends)


def PLTAXLine(XY1, paramPLT,XY2=(0,0), Slope=None):
    """
    Plots an infinite line defined by two points or a point and a slope.

    Args:
    - XY1 (tuple): Coordinates of the first point (x1, y1).
    - paramPLT (object): Object containing plot parameters.
    - XY2 (tuple): Coordinates of the second point (x2, y2). Default is (0, 0).
    - Slope (float): Slope of the line. If provided, XY2 is ignored.

    Returns:
    - None: This function does not return anything. It simply displays the line on the plot.
    """
    if Slope is not None:
        plt.axline(xy=XY1, slope=Slope,
                   color=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize,
                   marker=paramPLT.getMarker, markersize=paramPLT.getMarkerSize,
                   alpha=paramPLT.getAlpha, label=paramPLT.getLegends)
    else:
        plt.axline(xy1=XY1, xy2=XY2,
                   color=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize,
                   marker=paramPLT.getMarker, markersize=paramPLT.getMarkerSize,
                   alpha=paramPLT.getAlpha, label=paramPLT.getLegends)


def PLTCoordsSpan(ValMin, ValMax, paramPLT, SecValMin=0, SecValMax=1, BOrientation=True):
    """
    Plots a shaded span (rectangle) on the plot, either vertically or horizontally, based on the specified parameters.

    Args:
    - ValMin (float): Minimum value for the primary axis (x-axis for vertical span, y-axis for horizontal span).
    - ValMax (float): Maximum value for the primary axis (x-axis for vertical span, y-axis for horizontal span).
    - paramPLT (object): Object containing plot parameters.
    - SecValMin (float): Minimum value for the secondary axis (y-axis for vertical span, x-axis for horizontal span) and is in relative units (0 to 1).
    - SecValMax (float): Maximum value for the secondary axis (y-axis for vertical span, x-axis for horizontal span) and is in relative units (0 to 1).
    - BOrientation (bool): Boolean flag to specify the orientation of the span.
    """
    if BOrientation:  # Vertical line
        plt.axvspan(xmin=ValMin, xmax=ValMax, ymin=SecValMin, ymax=SecValMax,
                    facecolor=paramPLT.getColour, hatch=paramPLT.getHatch,
                    edgecolor=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize, alpha=paramPLT.getAlpha,
                    label=paramPLT.getLegends)

    elif BOrientation == False:
        plt.axhspan(ymin=ValMin, ymax=ValMax, xmin=SecValMin, xmax=SecValMax,
                    facecolor=paramPLT.getColour, hatch=paramPLT.getHatch,
                    edgecolor=paramPLT.getColour, linestyle=paramPLT.getLineType, linewidth=paramPLT.getLineSize, alpha=paramPLT.getAlpha,
                    label=paramPLT.getLegends)


def PLTFill(XValues, YValues, paramPLT, ValZOrder=0, YValuesSec=False):
    """
    Creates a filled plot between two curves (primary and secondary) using customizable parameters.

    Args:
    - XValues (list or array-like): X-axis values.
    - YValues (list or array-like): Y-axis values for the primary curve.
    - paramPLT (object): Object containing plot parameters.
    - ValZOrder (int): Z-order value to determine which layer is on top.
    - YValuesSec (list or array-like): Y-axis values for the secondary curve (optional).
    """
    if YValuesSec:
        plt.fill_between(XValues, YValues, YValuesSec,
                         facecolor=paramPLT.getColour, edgecolor=paramPLT.getColour,
                         hatch=paramPLT.getHatch, alpha=paramPLT.getAlpha, zorder=ValZOrder,
                         label=paramPLT.getLegends)
    else:
        plt.fill(XValues, YValues,
                 facecolor=paramPLT.getColour, edgecolor=paramPLT.getColour,
                 hatch=paramPLT.getHatch, alpha=paramPLT.getAlpha, zorder=ValZOrder,
                 label=paramPLT.getLegends)


def PLTBar(XBars, Heights, paramPLT, Width=0.8, StdErrors=None, BOrientation=True, Bottom=0):
    """
    Creates a bar plot with optional error bars, customizable Colours, labels, and orientation.

    Args:
    - XBars: List or array of x-coordinates for the bars or labels of each bar
    - Heights: List or array of heights for each bar or values of each bar
    - paramPLT: An object containing plot parameters 
    - Width: Width of each bar (default is 0.8) and can be specified for all bars or individually
    - StdErrors (optional): List or array of standard errors for each bar.
        - Scalar: Symmetric +/- error for all bars.
        - Shape (N,): Symmetric +/- error for each bar.
        - Shape (2, N): Asymmetric error values where:
            - First row specifies lower errors.
            - Second row specifies upper errors.
    - BOrientation: Boolean flag to specify the orientation of the bars.
        - True: Vertical bar plot (default).
        - False: Horizontal bar plot.
    - Bottom: Y-coordinate of the bottom of each bar (default is 0) and can be specified for all bars or individually

    Returns:
        None: This function does not return anything. It simply displays the bar plot.

    Improovements:
    
    """
    if BOrientation:
        # Scale type for Y axis
        if paramPLT.getYScaleType:
            BLogScale = True if paramPLT.getYScaleType == 'log' else False
        elif paramPLT.getGenericScaleType:
            BLogScale = True if paramPLT.getGenericScaleType == 'log' else False
        plt.bar(x=XBars, height=Heights, width=Width, yerr=StdErrors, ecolor='k',
                facecolor=paramPLT.getcolorFullList(BEmptying=False), edgecolor=paramPLT.getColourFullList(), 
                align='center', bottom=Bottom, label=paramPLT.getLegends)
    else:
        # Scale type for X axis
        if paramPLT.getXScaleType:
            BLogScale = True if paramPLT.getXScaleType == 'log' else False
        elif paramPLT.getGenericScaleType:
            BLogScale = True if paramPLT.getGenericScaleType == 'log' else False
        plt.barh(y=XBars, height=Width, width=Heights, yerr=StdErrors, ecolor='k',
                facecolor=paramPLT.getColourFullList(BEmptying=False), edgecolor=paramPLT.getColourFullList(), 
                align='center', left=Bottom, label=paramPLT.getLegends)


def PLTHist(XValues, paramPLT, NBins=0, HistType=0, BNormalizeArea=False, BStacked=False, BCumulative=False, Weights=None, HeightShift=None):
    """
    Creates a histogram plot using customizable parameters.
    
    Args:
    - XValues (list or array-like): Data values for the histogram.
    - paramPLT (object): Object containing plot parameters.
    - NBins (int): Number of bins or binning strategy:
        0: 'auto' (default)
        -1: 'fd' (Freedman-Diaconis Estimator)
        -2: 'doane' (Doane's formula)
        -3: 'scott' (Scott's rule)
        -4: 'stone' (Stone's rule)
        -5: 'rice' (Rice rule)
        -6: 'sturges' (Sturges' formula)
        -7: 'sqrt' (Square root choice)
        Or: Exact number of bins
    - HistType (int): Type of histogram:
        0: 'bar' (default)
        1: 'barstacked'
        2: 'step'
        3: 'stepfilled'
    - BNormalizeArea (bool): Whether to normalize the histogram area to 1.
    - BStacked (bool): Whether to stack multiple histograms.
    - BCumulative (bool): Whether to compute a cumulative histogram.
    - Weights (list or array-like): Weights for each value in XValues.
    - HeightShift (float): Value to shift the height of the histogram bars.

    Returns:
    - None: This function does not return anything. It simply displays the histogram.
    """
    # Dict to map NBins values to matplotlib options
    NBinsDIct = {0: 'auto', -1: 'fd', -2: 'doane', -3: 'scott', -4: 'stone', -5: 'rice', -6: 'sturges', -7: 'sqrt'}
    NBins = NBinsDIct.get(NBins, int(abs(NBins)))  # Default to absolute value if not in dict

    # Dict to map histogram type values to matplotlib options
    HistTypeDict = {0: 'bar', 1: 'barstacked', 2: 'step', 3: 'stepfilled'}
    HistType = HistTypeDict.get(HistType, 'bar')  # Default to 'bar' if not in dict
    
    # Scale type for Y axis
    if paramPLT.getYScaleType:
        BLogScale = True if paramPLT.getYScaleType == 'log' else False
    elif paramPLT.getGenericScaleType:
        BLogScale = True if paramPLT.getGenericScaleType == 'log' else False

    im = plt.hist(XValues, bins=NBins, density=BNormalizeArea, stacked=BStacked, cumulative=BCumulative, weights=Weights,
             bottom=HeightShift, histtype=HistType, align='mid', orientation='vertical', rwidth=None, log=BLogScale, 
             color=paramPLT.getColour, label=paramPLT.getLegends)

   
def PLTHist2D(XValues, YValues, paramPLT, NBins=10, BNormalizeArea=False, BCumulative=False, 
              CountMin=None, CountMax=None, ValMin=None, ValMax=None, Weights=None):
    """
    Creates a 2D histogram plot using customizable parameters.

    Args:
    - XValues (list or array-like): X-axis data values for the histogram.
    - YValues (list or array-like): Y-axis data values for the histogram.
    - paramPLT (object): Object containing plot parameters.
    - NBins : Number of bins:
        - If int, the number of bins for the two dimensions (nx = ny = bins).
        - If [int, int], the number of bins in each dimension (nx, ny = bins).
        - If array-like, the bin edges for the two dimensions (x_edges = y_edges = bins).
        - If [array, array], the bin edges in each dimension (x_edges, y_edges = bins)
    - BNormalizeArea (bool): Whether to normalize the histogram area to 1.
    - BCumulative (bool): Whether to compute a cumulative histogram.
    - Weights (list or array-like): Weights for each value in XValues and YValues.
    - CountMin (float): Minimum count threshold to display a bin.
    - CountMax (float): Maximum count threshold to display a bin.
    - ValMin (float): Minimum value for the Colour scale.
    - ValMax (float): Maximum value for the Colour scale.

    Returns:
    - None: This function does not return anything. It simply displays the 2D histogram.
    """

    counts, xedges, yedges, im = plt.hist2d(XValues, YValues, bins=NBins, density=BNormalizeArea, weights=Weights, cmin=CountMin, cmax=CountMax,
               cmap=paramPLT.getColourMap, norm=None, vmin=ValMin, vmax=ValMax, alpha=paramPLT.getAlpha)
    paramPLT.getMappable = im  # Store the mappable object for Colourbar


def PLTPie(Val, Labels, paramPLT, TypeAutopct=0, PrecisionPct=1, AbsUnit="", PrecisionAbs=0, 
           Radius=1, StartAngle=0, LabelDist=1.25, PctDist=0.6, BShadow=False, explode=None, 
           EnableAnnotations=False):
    """
    Creates a pie plot with customizable options, including optional annotations.

    Args:
    - Val (list): Values for the pie chart.
    - Labels (list): Labels for each slice of the pie chart.
    - paramPLT (object): Object containing plot parameters (e.g., getColour, getHatch).
    - TypeAutopct (int): Type of percentage display:
        0: Display only percentages (%).
        1: Display absolute values.
        2: Display both percentages and absolute values.
    - PrecisionPct (int): Decimal precision for percentages (e.g., 1 for 1 decimal place).
    - AbsUnit (str): Unit for absolute values (e.g., 'g', 'kg').
    - PrecisionAbs (int): Decimal precision for absolute values (e.g., 2 for 2 decimal places).
    - Radius (float): Radius of the pie chart.
    - StartAngle (float): Starting angle for the pie chart, in degrees.
    - LabelDist (float): Distance of labels from the center of the pie chart, as a fraction of the radius.
    - PctDist (float): Distance of percentage values from the center of the pie chart, as a fraction of the radius.
    - BShadow (bool): Whether to add a shadow effect to the pie chart.
    - explode (list): Fraction by which to offset a slice from the pie (e.g., [0, 0.1, 0, 0]).
    - EnableAnnotations (bool): Whether to add annotations (e.g., arrows and labels) to the pie chart.

    Returns:
    - Displays a pie chart.

    Improvements:
    - Ajouter des vérifications entre les paramètres pour éviter les conflits.
    - Extraire un nombre limité de paramètres pour éviter des clash si plus de valeurs.
    """

    paramPLT.getLegends = Labels
    paramPLT.getColour = [colors.to_rgba(c) for c in paramPLT.getColourFullList(BEmptying=True)]

    def GeneAutopct(pct, allvals):
        absolute = np.round(pct / 100. * np.sum(allvals), PrecisionAbs)
        if TypeAutopct <= 0:
            return f"{pct:.{PrecisionPct}f}%"
        elif TypeAutopct == 1:
            return f"{absolute:.{PrecisionAbs}f} {AbsUnit}"
        elif TypeAutopct == 2:
            return f""
        elif TypeAutopct >= 3:
            return f"{pct:.{PrecisionPct}f}%\n({absolute:.{PrecisionAbs}f} {AbsUnit})"

    # Generate the pie chart
    LLegends = paramPLT.getLegendsFullList(BEmptying=EnableAnnotations)
    wedges, texts, autotexts = plt.pie(Val, labels=paramPLT.getLegendsFullList(), labeldistance=LabelDist,
                                       autopct=lambda pct: GeneAutopct(pct, Val), pctdistance=PctDist,
                                       colors=paramPLT.getColourFullList(), hatch=paramPLT.getHatchFullList(),
                                       radius=Radius, startangle=StartAngle,
                                       explode=explode, shadow=BShadow,
                                       textprops=dict(size=paramPLT.getFontSize, color="k"))  # Customize text properties

    # Optional Annotation logic
    if EnableAnnotations:
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="w", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")
        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = f"angle,angleA=0,angleB={ang}"
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            plt.annotate(LLegends[i],  # Use legend text
                         xy=(x, y), 
                         xytext=(1.35 * Radius * np.sign(x), 1.4 * Radius * y),
                         fontsize=paramPLT.getFontSize,
                         horizontalalignment=horizontalalignment, 
                         **kw)

    # Remove axes and box for pie chart
    paramPLT.getXScaleType = 8
    paramPLT.getYScaleType = 8
    paramPLT.getBBox = False
    # Remove grid and legends
    paramPLT.getGridAxis = None
    paramPLT.getBLegends = False

def PLTImShow(ValMatrix, paramPLT, FInterpolType=0, BOrigin=True, BShowVal=True, Fmt=".2f"):
    """
    Displays an image plot of the provided matrix using custom parameters.
    """
    InterpolDict = {0: 'none', 1: 'auto', 2: 'nearest', 3: 'bilinear', 4: 'bicubic',
                    5: 'spline16', 6: 'spline36', 7: 'hanning', 8: 'hamming',
                    9: 'hermite', 10: 'kaiser', 11: 'quadric', 12: 'catrom',
                    13: 'gaussian', 14: 'bessel', 15: 'mitchell', 16: 'sinc', 17: 'lanczos',
                    18: 'blackman'}
    InterpolType = InterpolDict.get(FInterpolType, 'none')
    
    TypeOrigin =  'upper' if BOrigin else 'lower'

    plt.imshow(ValMatrix, cmap=paramPLT.getColourMap, alpha=paramPLT.getAlpha,
               norm=paramPLT.GenericScaleType, interpolation=InterpolType,
               origin=TypeOrigin)

    if BShowVal:
        Rows, Cols = ValMatrix.shape
        for i in range(Rows):
            for j in range(Cols):
                plt.text(j, i, format(ValMatrix[i, j], Fmt),
                         color="black",fontsize=paramPLT.getFontSize, fontweight="bold",
                         ha='center', va='center')

    PLTColourBar(paramPLT)

    

# 2D Shapes
def PLT2DCircle(x, y, NPoints, Radius, paramPLT, BFill=False):
    # Calculate the angles for the tick marks
    Angles = np.linspace(0, 2*np.pi, NPoints+1, endpoint=True)
    PreVal = False
    xEnd = 0
    yEnd = 0
    XPoint = []
    YPoint = []
    for Angle in Angles:
        # Starting point of the tick (on the circle)
        xStart = x + Radius*np.cos(Angle)
        yStart = y + Radius*np.sin(Angle)

        if PreVal:
            plt.plot([xStart, xEnd],
                     [yStart, yEnd],
                     color=paramPLT.getColour,
                     linestyle=paramPLT.getLineType,
                     marker=paramPLT.getMarker,
                     linewidth=paramPLT.getLineSize,
                     markersize=paramPLT.getLineSize,
                     label=paramPLT.getLegends)
            XPoint.append(xEnd)
            YPoint.append(yEnd)
        else:
            PreVal = True
        xEnd = xStart
        yEnd = yStart
    if BFill:
        plt.fill(XPoint, YPoint, color=paramPLT.getColour, zorder=0,
                 label=paramPLT.getLegends)

# Plotting functions in 3D
# 3D

# 3D Shapes


# Text management functions for matplotlib
def FormatText(Text, Fontsize=None, Weight=None, Style=None, Family=None,
                Colour=None, BackgroundColour=None, Alpha=None):
    """
    Applies text formatting options dynamically.
    If an option is None, it resets to the default Matplotlib setting.
    
    Args:
        Text: Matplotlib text object
        Fontsize: float or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}
        Weight: {'light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black'}
        Style: {'normal', 'italic', 'oblique'} or None
        Family: {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace'} or None
        Colour: Named Colour, hex ('#FF5733'), or RGB tuple ((1,0,0))
        BackgroundColour: Same as Colour
        Alpha: float (0.0 to 1.0, where 0 is fully transparent and 1 is opaque)
    """
    if Fontsize is not None:
        Text.set_fontsize(Fontsize)

    if Weight is not None:
        Text.set_weight(Weight)

    if Style is not None:
        Text.set_style(Style)

    if Family is not None:
        Text.set_family(Family)

    if Colour is not None:
        Text.set_color(Colour)

    if BackgroundColour is not None:
        Text.set_backgroundcolor(BackgroundColour)

    if Alpha is not None:
        Text.set_alpha(Alpha)