"""
Created by Mingrui Zhao @ 2017
define some classes and functions used throughout the project
"""
# Load module
import os
import shutil
import uuid
from colored import fg, bg, attr
import subprocess
import hashlib
import time
import tarfile

def generate_uuid():
    return uuid.uuid4().hex

def abspath(path):
    return os.path.abspath(path)

def project_path(path=None):
    """ Get the project path by searching for project.json
    """
    if (path is None):
        path = os.getcwd()
    while (path != "/"):
        if exists(path+"/.chern/project.json"):
            return path
        path = abspath(path+"/..")
    raise NotInChernRepoError("Not in a Chern repository.")

def dir_mtime(path):
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

def md5sum(filename, block_size=65536):
    md5 = hashlib.md5()
    with open(filename, 'rb') as file:
        for block in iter(lambda: file.read(block_size), b''):
            md5.update(block)
    return md5.hexdigest()

def dir_md5(directory_path):
    md5_hash = hashlib.md5()

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = md5sum(file_path)
            md5_hash.update(file_hash.encode('utf-8'))

    return md5_hash.hexdigest()

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
    return os.environ["HOME"] + "/.Chern/config.json"

def local_config_dir():
    return os.environ["HOME"] + "/.Chern"

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
    return files

def rm_tree(src):
    shutil.rmtree(src)

def copy_tree(src, dst):
    shutil.copytree(src, dst)

def exists(path):
    return os.path.exists(path)

def make_archive(filename, dir_name):
    with tarfile.open(filename+".tar.gz", "w:gz") as tar:
        tar.add(dir_name,
        arcname=os.path.basename(dir_name),)


def unpack_archive(filename, dir_name):
    shutil.unpack_archive(filename, dir_name, "zip")

def strip_path_string(path_string):
    """ Remove the "/" in the end of the string
    and the " " in the begin and the end of the string.
    replace the "." in the string to "/"
    """
    path_string = path_string.strip(" ")
    path_string = path_string.rstrip("/")
    return path_string

def refine_path(path, home):
    if path.startswith("~") or path.startswith("/"):
        path = home + path[1:]
    else:
        path = os.path.abspath(path)
    return path

def walk(top):
    d = list_dir(top)
    dirs = []
    files = []
    names = []
    for f in d:
        if f == ".chern": continue
        if f.startswith("."): continue
        if f.endswith("~undo-tree~"): continue
        if os.path.isdir(os.path.join(top, f)):
            dirs.append(f)
        else:
            names.append(f)
    yield ".", dirs, names
    for f in dirs:
        for path, dirs, names in os.walk(os.path.join(top, f)):
            path = os.path.relpath(path, top)
            if f.startswith("."): continue
            yield (path, dirs, names)

def tree_excluded(path):
    file_tree = []
    for dirpath, dirnames, filenames in walk(path):
        file_tree.append([dirpath, dirnames, filenames])
    return file_tree

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
    if color == "warning":
        return "\033[31m" + string + "\033[m"
    if color == "debug":
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
