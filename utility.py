# @section: IMPORTS
import math

numericType = int | float

def inRange(value: numericType, lower: numericType, upper: numericType):
    return lower <= value < upper

def wrap(value: numericType, lower: numericType, upper: numericType):
    if inRange(value, lower, upper): return value
    elif value < lower: return upper - 1
    elif value >= upper: return lower

def clamp(value: numericType, lower: numericType, upper: numericType):
    return min(max(value, lower), upper)

def normalize(array: list[numericType]):
    norm = math.sqrt(map(lambda x : x * x, array))
    return map(lambda x: x / norm, array)

def arrDiff(arr1: list[numericType], arr2):
    if len(arr1) != len(arr2): return 0
    total = 0
    for i in range(len(arr1)):
        total += arr1[i] - arr2[i]

    return abs(total)