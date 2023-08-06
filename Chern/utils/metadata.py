import json
import os
import yaml

class ConfigFile(object):
    """ ConfigFile class, it is used to read and write the metadata.
    In the version 3 of ``Chern'', metadata is saved in a json file rather than a python file.
    It will support three types:
        dict,
        list,
          and
        string
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
        with open(file_path, encoding='utf-8') as f:
            contents = f.read()
            if contents == "" or contents.isspace():
                return default
            d = json.loads(contents)
            return d.get(variable_name, default)

    def write_variable(self, variable_name, value):
        file_path = self.file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)
        try_times = 10 ** 4
        for i in range(try_times):
            if not os.path.exists(file_path + ".lock"):
                break
        if os.path.exists(file_path + ".lock"):
            raise os.error

        open(file_path+".lock", "a").close()

        with open(file_path, encoding='utf-8') as f:
            contents = f.read()
            if contents == "" or contents.isspace():
                d = {}
            else:
                d = json.loads(contents)

        d[variable_name] = value
        with open(file_path, "w") as f:
            json.dump(d, f)

        os.remove(file_path+".lock")

class YamlFile(object):
    """ ConfigFile class, it is used to read and write the metadata.
    yaml file is similar to json, but it is somewhat more-human readable
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
        with open(file_path, encoding='utf-8') as f:
            contents = f.read()
            if contents == "" or contents.isspace():
                return default
            d = yaml.load(contents, Loader=yaml.Loader)
            return d.get(variable_name, default)

    def write_variable(self, variable_name, value):
        file_path = self.file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)
        try_times = 10 ** 4
        for i in range(try_times):
            if not os.path.exists(file_path + ".lock"):
                break
        if os.path.exists(file_path + ".lock"):
            raise os.error

        open(file_path+".lock", "a").close()

        with open(file_path, encoding='utf-8') as f:
            contents = f.read()
            if contents == "" or contents.isspace():
                d = {}
            else:
                d = yaml.load(contents, Loader=yaml.Loader)

        d[variable_name] = value
        with open(file_path, "w") as f:
            yaml.dump(d, f)

        os.remove(file_path+".lock")
