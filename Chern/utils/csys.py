"""
Created by Mingrui Zhao @ 2017
define some classes and functions used throughout the project
"""
# Load module
import os
import shutil
import uuid
from colored import fg, attr
import hashlib
import tarfile
import subprocess
from contextlib import contextmanager

# Utility Functions
def generate_uuid():
    """ Generate a uuid
    """
    return uuid.uuid4().hex


def colorize(string, color):
    """ Make the string have color
    """
    if color == "warning":
        return "\033[31m" + string + "\033[m"
    if color == "debug":
        return "\033[31m" + string + "\033[m"
    elif color == "comment":
        return fg("blue") + string + attr("reset")
    elif color == "title0":
        return fg("red")+attr("bold")+string+attr("reset")
    return string


def color_print(string, color):
    """ Print the string with color
    """
    print(colorize(string, color))


def debug(*arg):
    """ Print debug string
    """
    print(colorize("debug >> ", "debug"), end="")
    for s in arg:
        print(colorize(s.__str__(), "debug"), end=" ")
    print("*")


# Path and Directory Functions
def abspath(path):
    """ Get the absolute path of the path
    """
    return os.path.abspath(path)


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


def refine_path(path, home):
    """ Refine the path
    """
    if path.startswith("~") or path.startswith("/"):
        path = home + path[1:]
    else:
        path = os.path.abspath(path)
    return path


def exists(path):
    """ Check if the path exists
    """
    return os.path.exists(path)


def mkdir(directory):
    """ Safely make directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def list_dir(src):
    """ List the files in the directory
    """
    files = os.listdir(src)
    return files


def walk(top):
    """ Walk the directory
    """
    d = list_dir(top)
    dirs = []
    names = []
    for f in d:
        if f == ".chern":
            continue
        if f.startswith("."):
            continue
        if f.endswith("~undo-tree~"):
            continue
        if os.path.isdir(os.path.join(top, f)):
            dirs.append(f)
        else:
            names.append(f)
    yield ".", dirs, names
    for f in dirs:
        for path, dirs, names in os.walk(os.path.join(top, f)):
            path = os.path.relpath(path, top)
            if f.startswith("."):
                continue
            yield (path, dirs, names)


def tree_excluded(path):
    """ Get the file tree
    """
    file_tree = []
    for dirpath, dirnames, filenames in walk(path):
        file_tree.append([dirpath, dirnames, filenames])
    return file_tree


def project_path(path=None):
    """ Get the project path by searching for project.json
    """
    if path is None:
        path = os.getcwd()
    if not os.path.exists(path):
        return None
    while path != "/":
        if exists(path+"/.chern/project.json"):
            return abspath(path)
        path = abspath(path+"/..")
    return None


def dir_mtime(path):
    """ Get the latest modified time of the directory
    """
    mtime = os.path.getmtime(path)
    if path.endswith(".chern"):
        mtime = -1
    if not os.path.isdir(path):
        return mtime
    for sub_dir in os.listdir(path):
        if sub_dir == ".git":
            continue
        mtime = max(mtime, dir_mtime(os.path.join(path, sub_dir)))
    return mtime


def daemon_path():
    """ Get the daemon path
    """
    path = os.environ["HOME"] + "/.Chern/daemon"
    mkdir(path)
    return path


def local_config_path():
    """ Get the local config path
    """
    return os.environ["HOME"] + "/.Chern/config.json"


def local_config_dir():
    """ Get the local config directory
    """
    return os.environ["HOME"] + "/.Chern"


# File Operations
def copy(src, dst):
    """ Safely copy file
    """
    directory = os.path.dirname(dst)
    mkdir(directory)
    shutil.copy2(src, dst)


def rm_tree(src):
    """ Remove the directory
    """
    shutil.rmtree(src)


def copy_tree(src, dst):
    """ Copy the directory
    """
    shutil.copytree(src, dst)


def make_archive(filename, dir_name):
    """ Make the tar.gz file
    """
    with tarfile.open(filename+".tar.gz", "w:gz") as tar:
        tar.add(
            dir_name,
            arcname=os.path.basename(dir_name)
        )


def unpack_archive(filename, dir_name):
    """ Unpack the tar.gz file
    """
    shutil.unpack_archive(filename, dir_name, "tar")


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
        except OSError:
            pass
    else:
        try:
            shutil.rmtree(file_path[:index] + "/__pycache__")
        except OSError:
            pass


# Checksum Functions
def md5sum(filename, block_size=65536):
    """ Get the md5sum of the file
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as file:
        for block in iter(lambda: file.read(block_size), b''):
            md5.update(block)
    return md5.hexdigest()


def dir_md5(directory_path):
    """ Get the md5sum of the directory
    """
    md5_hash = hashlib.md5()

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = md5sum(file_path)
            md5_hash.update(file_hash.encode('utf-8'))

    return md5_hash.hexdigest()

@contextmanager
def open_subprocess(command):
    # Create the subprocess
    process = subprocess.Popen(command, shell=True)
    try:
        # Yield the process to the 'with' block
        yield process
    finally:
        # Ensure the subprocess is finished and cleaned up
        process.wait()
