from Chern.utils import metadata
from logging import getLogger
from os.path import join

logger = getLogger("ChernLogger")


class SettingManager:
    # Reading Settings
    def environment(self):
        """
        Read the environment file
        """
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        environment = parameters_file.read_variable("environment", "")
        return environment

    def memory_limit(self):
        """
        Read the memory limit file
        """
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        memory_limit = parameters_file.read_variable(
            "kubernetes_memory_limit", "")
        return memory_limit

    def parameters(self):
        """
        Read the parameters file
        """
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        parameters = parameters_file.read_variable("parameters", {})
        return sorted(parameters.keys()), parameters

    def auto_download(self):
        """
        Return whether the task is auto_download or not
        """
        return self.config_file.read_variable("auto_download", True)

    def default_runner(self):
        """
        Return the default runner
        """
        return self.config_file.read_variable("default_runner", "local")

    # Modifying Settings
    def add_parameter(self, parameter, value):
        """
        Add a parameter to the parameters file
        """
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        parameters = parameters_file.read_variable("parameters", {})
        parameters[parameter] = value
        parameters_file.write_variable("parameters", parameters)

    def remove_parameter(self, parameter):
        """
        Remove a parameter to the parameters file
        """
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        parameters = parameters_file.read_variable("parameters", {})
        if parameter not in parameters.keys():
            print("Parameter not found")
            return
        parameters.pop(parameter)
        parameters_file.write_variable("parameters", parameters)

    def set_auto_download(self, auto_download):
        """
        Set the auto_download
        """
        self.config_file.write_variable("auto_download", auto_download)

    def set_default_runner(self, runner):
        """
        Set the default runner
        """
        self.config_file.write_variable("default_runner", runner)

    # Validation
    def env_validated(self):
        """
        Check whether the environment is validated or not
        """
        if self.environment() == "rawdata":
            return True
        if self.algorithm() is not None:
            if self.environment() == self.algorithm().environment():
                return True
        return False

    def validated(self):
        """
        Check whether the task is validated or not
        """
        if self.environment() == "rawdata":
            return True
        if self.algorithm() is not None:
            if self.environment() == self.algorithm().environment():
                return False
        return True
