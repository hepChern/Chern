""" VAlgorithm
"""
import os
import shutil
import subprocess

from ..utils import csys
from ..utils.pretty import colorize
from ..utils import metadata

from .chern_cache import ChernCache
from .chern_communicator import ChernCommunicator
from . import helpme
from .vobject import VObject
from .vobj_file import LsParameters

CHERN_CACHE = ChernCache.instance()


class VAlgorithm(VObject):
    """ Algorithm class
    """

    def helpme(self, command):
        """ Helpme function """
        print(helpme.algorithm_helpme.get(command, "No such command, try ``helpme'' alone."))

    def print_status(self):
        """ Print the status """
        super().print_status()
        cherncc = ChernCommunicator.instance()
        workflow_check = cherncc.workflow(self.impression())
        if workflow_check == "UNDEFINED":
            print("Workflow not defined")

    def run_status(self):
        """ Asking for the remote status
        """
        cherncc = ChernCommunicator.instance()
        return cherncc.status(self.impression())

    def is_submitted(self, runner="local"):
        """ Judge whether submitted or not. Return a True or False.
        [FIXME: incomplete]
        """
        if not self.is_impressed_fast():
            return False
        return False

    def resubmit(self, runner="local"):
        """ Resubmit """
        # FIXME: fixit later


    def ls(self, show_info=LsParameters()):
        """ list the infomation.
        """
        super().ls(show_info)

        if show_info.status:
            status = self.status()
            status_color = ""
            if status == "new":
                status_color = "normal"
            elif status == "impressed":
                status_color = "success"

            status_str = colorize("["+status+"]")
            print(colorize("**** STATUS:", "title0"), status_str)

        self.print_files(self.path, excluded=[".chern", "chern.yaml", "README.md"])

        environment = self.environment()
        print(colorize("---- Environment:", "title0"), environment)

        build_commands = self.build_commands()
        if build_commands:
            print(colorize("---- Build commands:", "title0"))
            for command in build_commands:
                print(command)

        commands = self.commands()
        if commands:
            print(colorize("---- Commands:", "title0"))
            for command in commands:
                print(command)


    def print_files(self, path, excluded=[]):
        """ Print the files in the path """
        print(colorize("---- Files:", "title0"))
        files = [f for f in os.listdir(path) if not f.startswith(".") and f not in excluded]

        if not files:
            print("No files found.")
            return

        # Determine terminal width
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        max_length = max(len(f) for f in files) + 2  # Padding
        # Calculate number of columns
        num_columns = max(1, terminal_width // max_length)
        # Print files in columns
        for i, f in enumerate(files):
            print(f.ljust(max_length), end="\n" if (i + 1) % num_columns == 0 else "")
        print()

    def commands(self):
        """ Get the commands from the yaml file """
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        return yaml_file.read_variable("commands", [])

    def build_commands(self):
        """ Get the build commands from the yaml file """
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        return yaml_file.read_variable("build", [])

    def environment(self):
        """ Get the environment
        """
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        return yaml_file.read_variable("environment", "")

def create_algorithm(path, use_template=False):
    """ Create an algorithm """
    path = csys.strip_path_string(path)
    os.mkdir(path)
    os.mkdir(f"{path}/.chern")
    config_file = metadata.ConfigFile(f"{path}/.chern/config.json")
    config_file.write_variable("object_type", "algorithm")

    with open(f"{path}/.chern/README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write("Please write README for this algorithm")
    subprocess.call(f"vim {path}/.chern/README.md", shell=True)
    if use_template:
        template_name = input("Please input the Dockerfile template type")
        print("Creating template, but ...")
        print("Not implemented yet.")
        print(f"Template name: {template_name}")
        # FIXME: implement it later
