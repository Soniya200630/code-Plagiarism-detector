# Demo file for the "Shorten" feature: intentionally wordy and repetitive.
import os
import math
import random


def square_all(numbers):
    """Return a list with every number squared."""
    result = []
    for n in numbers:
        result.append(n * n)
    return result


def even_numbers(numbers):
    """Return only the even numbers."""
    evens = []
    for value in numbers:
        if value % 2 == 0:
            evens.append(value)
    return evens


def is_adult(age):
    # check if a person is an adult
    if age >= 18:
        return True
    else:
        return False


def is_teen(age):
    if age >= 13 and age < 20:
        return True
    return False


def is_negative(x):
    if x < 0:
        return True
    return False


def is_below_zero(x):
    if x < 0:
        return True
    return False


def circle_area(radius):
    area = math.pi * radius * radius
    return area
    print("this line can never run")


def greet(name):
    if True:
        message = "Hello, " + name
    else:
        message = "never used"
    pass
    return message
