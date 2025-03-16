""" Core class for vtasks.
    + helpme: Print help message for the command.
    + ls: List the information of the task.
"""
# pylint: disable=too-many-public-methods

from abc import abstractmethod
from ..utils import metadata
from ..utils import csys
from .ChernCommunicator import ChernCommunicator

import Chern.kernel.vtask as vtsk
from logging import getLogger
import os
from os.path import join
from .vobject import VObject
from .vobj_core import LsParameters

logger = getLogger("ChernLogger")


class Core(VObject):
    """ Core class for vtasks.
    """
    def helpme(self, command):
        """ Print help message for the command.
        """
        from .helpme import task_helpme
        print(task_helpme.get(command, "No such command, try ``helpme'' alone."))

    def ls(self, show_info=LsParameters()):
        """ List the information of the task.
        """
        super(VTask, self).ls(show_info)
        parameters, values = self.parameters()
        if parameters != []:
            print(colorize("---- Parameters:", "title0"))
        for parameter in parameters:
            print(parameter, end=" = ")
            print(values[parameter])

        if self.environment() == "rawdata":
            print("Input data: {}".format(self.input_md5()))

        print(colorize("---- Environment:", "title0"), self.environment())
        print(colorize("---- Memory limit:", "title0"), self.memory_limit())
        if self.validated():
            print(colorize("---- Validated:", "title0"), colorize("True", "success"))
        else:
            print(colorize("---- Validated:", "title0"), colorize("False", "warning"))

        print(colorize("---- Auto download:", "title0"), self.auto_download())
        print(colorize("---- Default runner:", "title0"), self.default_runner())

        if show_info.status:
            status = self.status()
            if status == "new":
                status_color = "normal"
            elif status == "impressed":
                status_color = "success"

            status_str = colorize("["+status+"]", status_color)

            if status == "impressed":
                run_status = self.run_status()
                if run_status != "unconnected":
                    if run_status == "unsubmitted":
                        status_color = "warning"
                    elif run_status == "failed":
                        status_color = "warning"
                    else:
                        status_color = "success"
                    status_str += colorize("["+run_status+"]", status_color)
            print(colorize("**** STATUS:", "title0"), status_str)

        if self.is_submitted():
            print(colorize("---- Files:", "title0"))
            files = self.output_files()
            if files != []:
                files.sort()
                max_len = max([len(s) for s in files])
                columns = os.get_terminal_size().columns
                nfiles = columns // (max_len+4+7)
                for i, f in enumerate(files):
                    if not f.startswith(".") and f != "README.md":
                        print(("local:{:<"+str(max_len+4)+"}").format(f), end="")
                        if (i+1) % nfiles == 0:
                            print("")
                print("")

        if self.algorithm() is not None:
            print(colorize("---- Algorithm files:", "title0"))
            files = os.listdir(self.algorithm().path)
            if files == []:
                return
            files.sort()
            max_len = max([len(s) for s in files])
            columns = os.get_terminal_size().columns
            nfiles = columns // (max_len+4+11)
            count = 0
            for i, f in enumerate(files):
                count += 1
                if f.startswith("."):
                    continue
                if f == "README.md":
                    continue
                if f == "chern.yaml":
                    continue
                print(("algorithm:{:<"+str(max_len+4)+"}").format(f), end="")
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

    @abstractmethod
    def algorithm(self):
        """ Abstract method for future implementation"""
