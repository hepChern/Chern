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

class ConfigFile(object):
    """ ConfigFile class
    ConfigFile(somefile.py) can define a config file,
    where you can read and write python variables
    """
    def __init__(self, file_path):
        """ Initialize the class use a path
        Create a file if it is not initially exists
        """
        self.file_path = file_path

    def read_variable(self, variable_name, default=None):
        """ Get the content of some variable
        """
        file_path = self.file_path
        if not os.path.exists(file_path):
            return default
        # read the module
        from imp import load_source
        module = load_source("tmp_module_{0}".format(uuid.uuid4().hex), file_path)
        value = module.__dict__.get(variable_name, default)

        # remove pyc file and module instance
        remove_cache(file_path)
        del module
        return value

    def write_variable(self, variable_name, value):
        file_path = self.file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            open(file_path, "w").close()
        try_times = 10 ** 4
        for i in range(try_times):
            if not os.path.exists(file_path + ".lock"):
                break
        if os.path.exists(file_path + ".lock"):
            raise os.error

        open(file_path+".lock", "a").close()

        # Module variables, key value mapping
        from imp import load_source
        module = load_source("tmp_module_{0}".format(uuid.uuid4().hex), file_path)
        dic = module.__dict__

        # Add new variables to the list
        old_variables = dir(module)
        # DELETE print old_variables
        if variable_name not in old_variables:
            old_variables.append(variable_name)

        f = open(file_path, "w")
        # Change values
        dic[variable_name] = value

        # Save to file
        for key in old_variables:
            if not key.startswith("__") and not key.startswith("-"):
                if type(dic[key]) == str:
                    f.write("%s=u'%s'\n"%(key, str(dic[key])))
                elif type(dic[key]) == str:
                    f.write("%s='%s'\n"%(key, str(dic[key])))
                else:
                    f.write("%s=%s\n"%(key, str(dic[key])))
        # DELETED print "written"
        f.close()
        os.remove(file_path+".lock")
        del module
        remove_cache(file_path)

    def modify_variable(self):
        """
        Might be used in the future
        FIXME
        """
        pass
