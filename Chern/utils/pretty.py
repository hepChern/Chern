"""
Created by Mingrui Zhao @ 2017
define some classes and functions used throughout the project
"""
# Load module
from colored import fg, attr

def colorize(string, color):
    """Make the string have color"""
    colors = {
        "success": fg("green") + string + attr("reset"),
        "normal": fg("blue") + string + attr("reset"),
        "running": fg("yellow") + string + attr("reset"),
        "warning": "\033[31m" + string + "\033[m",
        "debug": "\033[31m" + string + "\033[m",
        "comment": fg("blue") + string + attr("reset"),
        "title0": fg("red") + attr("bold") + string + attr("reset")
    }
    return colors.get(color, string)  # Default to 'string' if color not found

def color_print(string, color):
    """Print the string with color"""
    print(colorize(string, color))
