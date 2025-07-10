# pylint: disable=too-many-public-methods
""" Core class for vtasks.
    + helpme: Print help message for the command.
    + ls: List the information of the task.
"""

import os
from abc import abstractmethod
from logging import getLogger

from . import helpme
from ..utils.pretty import colorize
from ..utils.message import Message
from .vobject import VObject
from .vobj_file import LsParameters

logger = getLogger("ChernLogger")


class Core(VObject):
    """ Core class for vtasks.
    """
    def helpme(self, command):
        """ Print help message for the command.
        """
        message = Message()
        message.add(helpme.task_helpme.get(command, "No such command, try ``helpme'' alone."))
        return message

    def ls(self, show_info=LsParameters()):
        """ List the information of the task.
        """
        super().ls(show_info)

        self.show_parameters()

        if show_info.status:
            self.show_status()

        # if self.is_submitted():
        #   self.show_submission()

        if self.algorithm() is not None:
            self.show_algorithm()

    def show_parameters(self):
        """ Show the parameters of the task.
        """
        parameters, values = self.parameters()
        if parameters != []:
            print(colorize("---- Parameters:", "title0"))
        for parameter in parameters:
            print(parameter, end=" = ")
            print(values[parameter])

        if self.environment() == "rawdata":
            print(colorize("---- Input data:", "title0"), self.input_md5())

        print(colorize("---- Environment:", "title0"), self.environment())
        print(colorize("---- Memory limit:", "title0"), self.memory_limit())
        if self.validated():
            print(colorize("---- Validated:", "title0"), colorize("true"))
        else:
            print(colorize("---- Validated:", "title0"), colorize("false"))

        print(colorize("---- Auto download:", "title0"), self.auto_download())
        print(colorize("---- Default runner:", "title0"), self.default_runner())

    def show_algorithm(self):
        """ Show the algorithm of the task.
        """
        print(colorize("---- Algorithm files:", "title0"))
        files = os.listdir(self.algorithm().path)
        if files == []:
            return
        files.sort()
        max_len = max(len(s) for s in files)
        columns = os.get_terminal_size().columns
        nfiles = columns // (max_len+4+11)
        count = 0
        for f in files:
            count += 1
            if f.startswith("."):
                continue
            if f == "README.md":
                continue
            if f == "chern.yaml":
                continue
            print(f"algorithm:{f:<{max_len+4}}", end="")
            if count % nfiles == 0:
                print("")
        if count % nfiles != 0:
            print("")
        print(colorize("---- Commands:", "title0"))
        for command in self.algorithm().commands():
            parameters, values = self.parameters()
            for parameter in parameters:
                parname = "${" + parameter + "}"
                command = command.replace(parname, values[parameter])
            print(command)

    def show_submission(self):
        """ Show the submission of the task.
        """
        print(colorize("---- Files:", "title0"))
        files = self.output_files()
        if files != []:
            files.sort()
            max_len = max(len(s) for s in files)
            columns = os.get_terminal_size().columns
            nfiles = columns // (max_len+4+7)
            for i, f in enumerate(files):
                if not f.startswith(".") and f != "README.md":
                    print(f"local:{f:<{max_len+4}}", end="")
                    if (i+1) % nfiles == 0:
                        print("")
            print("")

    @abstractmethod
    def get_task(self, path):
        """ Get the task from the path.
        """

    @abstractmethod
    def algorithm(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def parameters(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def input_md5(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def set_input_md5(self, path):
        """ Abstract method for future implementation"""

    @abstractmethod
    def output_files(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def environment(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def memory_limit(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def validated(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def auto_download(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def default_runner(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def send_data(self, path):
        """ Abstract method for future implementation"""
