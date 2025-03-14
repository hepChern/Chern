""" The VTask class
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Methods:
        + helpme:
            Print the helpme of the task
        + ls:
            First call the general ls and then print some other useful information:
            parameters, status, outputs, algorithms
        + output_files:
            Get the information of the output_files from ChernCommunicator
        + get_file:
            Get file??? from ChernCommunicator

        + inputs:
        + outputs:

        + submit
            Submit the job to server. Through ChernCommunicator.
        + resubmit
            Resubmit the job to server. Through ChernCommunicator.
        + view
        + cp
            Copy the output to some directory
        + remove
            Remove the task.
        + jobs
            Query the jobs of the task throught ChernCommunicator.

        + view
            Open the file through ChernCommunicator. This is quite temporatory. Because it can only open local file.

        + is_submitted:
            Judge whether the task is submitted or not. Ask this information from ChernCommunicator.

        + output_md5:
            Read the md5 of the output directory

        + add_parameter
        + remove_parameter:
            Add/Remove parameter, should deal the problem of missing parameter/parameter already there.

        + add_input
            Add input to the task(with alias), print something, maybe changed later.
        + remove_input
            Remove input of the task through alias.

        + add_algorithm
            Add the algorithm correspnding to the task. if already has algorithm, replace the old one and print the message. Maybe changed later
            because I do not want to print anything in the kernel.
        + remove_algorithm
            Remove the algorithm corresponding to the task. if nothing to remove it print the message. Maybe changed later because I do
            not want to print anything in the kernel.
        + algorithm
            Return the algorithm corresponding to this task. If the task is not related to an algorithm, return None.

        + container
            Return the container corresponding the top impression.
        + add_source
            Make a new task, with raw data.

        ===================
        Inherited from VObject
        + __init__
        + __str__, __repr__
        + invariant_path, relative_path
        + object_type, is_zombine
        + color_tag
        + ls
        + copy_to, clean_impressions/flow
        + rm
        + move_to
        + alias(and related)
        + add/remove_arc_from/to
        + (has)successor/predecessors(s)
        + doctor
        + pack(and related)
        + impression(and related)

"""
import os
import subprocess
from .VObject import VObject
# from Chern.kernel.VContainer import VContainer
from ..utils import utils
from ..utils import metadata
from ..utils import csys
from ..utils.pretty import colorize

from .ChernCache import ChernCache
from .ChernCommunicator import ChernCommunicator
from logging import getLogger
from os.path import join

from .vtask_input import InputManager
from .vtask_setting import SettingManager
from .vtask_core import Core
from .vtask_file import FileManager

cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class VTask(VObject, Core, InputManager, SettingManager, FileManager):
    def output_files(self):
        # FIXME, to get the output files list
        return []
        cherncc = ChernCommunicator.instance()
        return cherncc.output_files("local", self.impression())

    def get_file(self, filename):
        cherncc = ChernCommunicator.instance()
        return cherncc.get_file("local", self.impression(), filename)

    def view(self, filename):
        if filename.startswith("local:"):
            path = self.get_file("local:", filename[6:])
            if not csys.exists(path):
                print("File: {} do not exists".format(path))
                return
            subprocess.Popen("open {}".format(path), shell=True)

    def print_status(self):
        print("Status of task: {}".format(self.invariant_path()))
        if self.status() == "impressed":
            print("Impression: [{}]".format(colorize(self.impression().uuid, "success")))
        else:
            print("Impression: [{}]".format(colorize("New", "warning")))
            return
        cherncc = ChernCommunicator.instance()
        dite_status = cherncc.dite_status()
        if dite_status == "ok":
            print("DIET: [{}]".format(colorize("connected", "success")))
        else:
            print("DIET: [{}]".format(colorize("unconnected", "warning")))
            return

        deposited = cherncc.is_deposited(self.impression())
        if deposited == "FALSE":
            print("Impression not deposited in DIET")
            return

        environment = self.environment()
        if environment == "rawdata":
            run_status = self.run_status()
            print("Sample status: [{}]".format(colorize(run_status, "success")))
            files = cherncc.output_files(self.impression(), "none")
            print("Sample files (collected on DIET):")
            for f in files:
                print("    {}".format(f))
            return

        workflow_check = cherncc.workflow(self.impression())
        if workflow_check == "UNDEFINED":
            print("Workflow not defined")
            return

        if environment != "rawdata":
            print(colorize("**** WORKFLOW:", "title0"))
            runner = workflow_check[0]
            workflow = workflow_check[1]
            print("Workflow: [{}][{}]".format(colorize(runner,"success"), colorize(workflow, "success")))

            files = cherncc.output_files(self.impression(), runner)
            print("Output files (collected on DIET):")
            for f in files:
                print("    {}".format(f))

    def status(self, consult_id=None, detailed=False):
        """ Consult the status of the object
            There should be only two status locally: new|impressed
        """
        # If it is already asked, just give us the answer
        logger.debug("VTask status: Consulting status of {}".format(self.path))
        if consult_id:
            consult_table = cherncache.status_consult_table
            cid, status = consult_table.get(self.path, (-1,-1))
            if cid == consult_id:
                return status

        if not self.is_impressed_fast():
            if consult_id:
                consult_table[self.path] = (consult_id, "new")
            return "new"

        status = "impressed"
        if consult_id:
            consult_table[self.path] = (consult_id, status)
        return status


def create_task(path):
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(join(path, ".."))
    object_type = VObject(parent_path).object_type()
    if object_type != "project" and object_type != "directory":
        return

    csys.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path + "/.chern/config.json")
    config_file.write_variable("object_type", "task")
    config_file.write_variable("auto_download", True)
    config_file.write_variable("default_runner", "local")
    task = VObject(path)

    # Create the default chern.yaml file
    yaml_file = metadata.YamlFile(join(path, "chern.yaml"))
    yaml_file.write_variable("environment", "reanahub/reana-env-root6:6.18.04")
    yaml_file.write_variable("kubernetes_memory_limit", "256Mi")

    with open(path + "/.chern/README.md", "w") as f:
        f.write("Please write README for task {}".format(task.invariant_path()))


def create_data(path):
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(path+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "project" and object_type != "directory":
        return

    csys.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path + "/.chern/config.json")
    config_file.write_variable("object_type", "task")
    task = VObject(path)

    with open(path + "/.chern/README.md", "w") as f:
        f.write("Please write README for task {}".format(task.invariant_path()))

    yaml_file = metadata.YamlFile(join(path, "chern.yaml"))
    yaml_file.write_variable("environment", "rawdata")
    yaml_file.write_variable("uuid", "")
