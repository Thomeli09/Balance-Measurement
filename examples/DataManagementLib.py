# -*- coding: utf-8 -*-
"""
# Copyright (C) 2026 Thommes Eliott
#
# SPDX-License-Identifier: MIT
"""

# Data management function Library


# Other Lib
import numpy as np
import math


# Custom Lib


# General functions
def LenData(Data):
    """
    Count the number of elements in a given data structure.

    Args:
        data: tuple, list, numpy.ndarray, set, dict, or other iterable types
            The input data structure.

    Returns:
        int: Number of elements in the data structure.

    Raises:
        TypeError: If the data type is not supported.
    """
    if isinstance(Data, (tuple, list, set)):
        # For tuple, list, or set, simply return the length
        return len(Data)
    elif isinstance(Data, dict):
        # For dict, count the number of keys
        return len(Data.keys())
    elif isinstance(Data, np.ndarray):
        # For NumPy arrays, handle both row and column vectors
        if Data.ndim == 1:
            return Data.size
        elif Data.ndim == 2:
            # Row vector: shape (1, n), Column vector: shape (n, 1)
            if 1 in Data.shape:
                return Data.size
            else:
                print("Error: Data should not be a matrix.")
        else:
            print("Error: Data should not be a matrix.")
    elif hasattr(Data, '__len__'):
        # For other iterable types, try using len
        return len(Data)
    else:
        print(f"Error: Unsupported data type: {type(Data)}")
    return 0

def DataSort(L1, L2=None):
    """
    Sort list or array of numbers or pairs of values based on the first list.
    """
    if L2 is None:  # Sorting a list of numbers
        if isinstance(L1, np.ndarray):
            L1 = np.sort(L1)
        elif isinstance(L1, list):
            L1 = sorted(L1)
        return L1
    else:  # Sorting pairs of values based on the first list
        if LenData(L1)==LenData(L2):
            if isinstance(L1, np.ndarray) and isinstance(L2, np.ndarray):
                SortedIndices = np.argsort(L1)
                L1 = L1[SortedIndices]
                L2 = L2[SortedIndices]
            elif isinstance(L1, list) and isinstance(L2, list):
                L1, L2 = zip(*sorted(zip(L1, L2)))
            return L1, L2
        else:
            print("Error: The two lists should have the same length.")


# List management functions
def ListSort(L1, L2=False):
    """
    Sort a list of numbers or pairs of values based on the first list.
    """
    if not L2:  # Sorting a list of numbers
        L1 = sorted(L1)
        return L1
    else:  # Sorting pairs of values based on the first list
        if LenData(L1)==LenData(L2):
            L1, L2 = zip(*sorted(zip(L1, L2)))
            return L1, L2
        else:
            print("Error: The two lists should have the same length.")

def ListFindFirstMaxPair(L1, L2):
    """
    Finds the first occurrence of the maximum value in list1 
    and returns the paired value from list2.
    
    Args:
        L1 (list): The list to find the max value in.
        L2 (list): The paired list to retrieve the corresponding value.

    Returns:
        tuple: (max_value, paired_value) or None if lists are empty or mismatched.
    """
    if not L1 or not L2:
        print("Error: The two lists should be non-empty.")
        return None

    if not isinstance(L1,list) or not isinstance(L1,list):
        print("Error: The two inputs should be lists.")
        return None

    if len(L1) != len(L2):
        print("Error: The two lists should have the same length.")
        return None

    MaxIndex = L1.index(max(L1))  # Find the index of the first max value
    return L1[MaxIndex], L2[MaxIndex]  # Return (max_value, paired_value)

def ListMult(Val, ListVal, BPrint=True):
    """
    Multiply a list of values by a constant value.
    """
    MultListVal = [Val*i for i in ListVal]
    if BPrint:
        print("Multiplication of list by value:", MultListVal)
    return MultListVal

def ListSum(ListOfSumList, BPrint=True):
    """
    Sum a list of lists of values.
    """
    SumListVal = [sum(x) for x in zip(*ListOfSumList)]
    if BPrint:
        print("Sum of lists:", SumListVal)
    return SumListVal

def ListGCD(LVals):
    """
    Calculate the greatest common divisor (GCD) of a list of integers.

    Args:
        LVals (list): List of integers.
    """
    # Check if the list is empty
    if not LVals:
        print("Error: The list is empty.")
        return None

    # Check if the list contains only integers
    if not all(isinstance(i, int) for i in LVals):
        print("Warning : Not all elements are integers. The GCD will be calculated on rounded values.")
        LVals = [int(round(i)) for i in LVals]

    GCDVal = math.gcd(*LVals)
    return GCDVal

# Text management functions


# Vector management functions
def VectorSelectVal(Vector, Val, AbsTol=1e-6, BFirst=False):
    """
    Select values in a numpy array that are equal to a given value within a tolerance and return the indices.
    If BFirst is True, return the first occurrence only.
    """
    IndexVect = np.where(np.isclose(Vector, Val, atol=AbsTol))[0]
    SelectedVal = Vector[IndexVect]

    if BFirst:
        if IndexVect.size == 0:
            print("Error: Value not found.")
            return None, None
        IndexVect = IndexVect[0]
        SelectedVal = SelectedVal[0]

    return SelectedVal, IndexVect

def VectorSelectClosestVal(Vector, Val, BFirst=False):
    """
    Select values in a numpy array that are the closest to a given value and return the indices.
    If BFirst is True, return the first occurrence only.
    """
    IndexVect = np.argmin(np.abs(Vector - Val))
    SelectedVal = Vector[IndexVect]

    if IndexVect.size == 0:
        print("Error: Value not found.")

    return SelectedVal, IndexVect

def VectorSelectValInRange(Vector, ValMin, ValMax, IntPick=1, NPick=None):
    """
    Select values in a numpy array that are within a given range and return the indices.
    Args:
    - Vector: numpy array of values to select from
    - ValMin: minimum value of the range
    - ValMax: maximum value of the range
    - IntPick: Choose to pick one in every IntPick values in the selected range (default is 1, meaning all values are selected)
    - NPick: Number of values to pick in the selected range (overrides IntPick if specified)
    """
    IndexVect = np.where((Vector >= ValMin) & (Vector <= ValMax))[0]
    if IndexVect.size == 0:
        return np.array([]), np.array([], dtype=int)  # nicer than None for downstream

    if NPick is not None:
        if NPick <= 0:
            raise ValueError("NPick must be a positive integer.")
        if NPick < IndexVect.size:
            IndexVect = IndexVect[np.linspace(0, IndexVect.size - 1, NPick, dtype=int)]
        # else: keep all IndexVect (don’t fall back to IntPick)
    else:
        if IntPick <= 0:
            raise ValueError("IntPick must be >= 1.")
        IndexVect = IndexVect[::IntPick]
        
    SelectedVal = Vector[IndexVect]
    return SelectedVal, IndexVect


# Matrix management functions
def MatrixSelectRowOrColumn(Matrix, Index, Axis=0):
    """
    Select a row or column from a 2D numpy array.
    """
    # Check if the index is within the matrix dimensions
    if Axis == 0 and (Index >= Matrix.shape[0] or Index < 0):
        print("Error: Row index out of bounds.")
        return None
    elif Axis == 1 and (Index >= Matrix.shape[1] or Index < 0):
        print("Error: Column index out of bounds.")
        return None

    # Select the row or column
    if Axis == 0:  # Selecting a row
        return Matrix[Index, :]
    elif Axis == 1:  # Selecting a column
        return Matrix[:, Index]
    else:
        print("Error: Axis should be 0 or 1.")
        return None
