"""
Created by Mingrui Zhao @ 2017
define some classes and functions used throughout the project
"""
# Load module
import os
import shutil
import uuid
from colored import fg, bg, attr

def compress():
    # Compress a directory with the tar algorithm
    pass

def recompress():
    pass

def daemon_path():
    path = os.environ["HOME"] + "/.Chern/daemon"
    mkdir(path)
    return path

def profile_path():
    # FIXME
    return ""

def storage_path():
    # FIXME
    path = os.environ["HOME"] + "/.Chern/Storage"
    mkdir(path)
    return path

def local_config_path():
    return os.environ["HOME"] + "/.Chern/config.py"

def local_config_dir():
    return os.environ["HOME"] + "/.Chern/config.py"

def mkdir(directory):
    """ Safely make directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def copy(src, dst):
    """ Saftly copy file
    """
    directory = os.path.dirname(dst)
    mkdir(directory)
    shutil.copy2(src, dst)

def list_dir(src):
    files = os.listdir(src)

def copy_tree(src, dst):
    shutil.copytree(src, dst)

def strip_path_string(path_string):
    """ Remove the "/" in the end of the string
    and the " " in the begin and the end of the string.
    replace the "." in the string to "/"
    """
    path_string = path_string.strip(" ")
    path_string = path_string.rstrip("/")
    return path_string

def special_path_string(path_string):
    """ Replace the path string . -> /
    rather than the following cases
    .
    ..
    path/./../
    """
    if path_string.startswith("."):
        return path_string
    if path_string.find("/.") != -1:
        return path_string
    return path_string.replace(".", "/")

def colorize(string, color):
    """ Make the string have color
    """
    if color == "success":
        return fg("green")+string+attr("reset")
    elif color == "normal":
        return string
    elif color == "warning":
        return "\033[31m" + string + "\033[m"
    elif color == "debug":
        return "\033[31m" + string + "\033[m"
    elif color == "comment":
        return fg("blue")+ string +attr("reset")
    elif color == "title0":
        return fg("red")+attr("bold")+string+attr("reset")
    return string

def color_print(string, color):
    print(colorize(string, color))

def debug(*arg):
    """ Print debug string
    """
    print(colorize("debug >> ", "debug"), end="")
    for s in arg:
        print(colorize(s.__str__(), "debug"), end=" ")
    print("*")

def remove_cache(file_path):
    """ Remove the python cache file *.pyc *.pyo *.__pycache
    file_path = somewhere/somename.py
            or  somename.py
    """
    file_path = strip_path_string(file_path)
    if os.path.exists(file_path+"c"):
        os.remove(file_path+"c")
    if os.path.exists(file_path+"o"):
        os.remove(file_path+"o")
    index = file_path.rfind("/")
    if index == -1:
        try:
            shutil.rmtree("__pycache__")
        except:
            pass
    else:
        try:
            shutil.rmtree(file_path[:index] + "/__pycache__")
        except:
            pass
