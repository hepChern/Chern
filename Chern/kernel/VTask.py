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
            Open the file through ChernCommunicator. This is quite temporatory.
            Because it can only open local file.

        + is_submitted:
            Judge whether the task is submitted or not. Ask this information from
            ChernCommunicator.

        + output_md5:
            Read the md5 of the output directory

        + add_parameter
        + remove_parameter:
            Add/Remove parameter, should deal the problem of missing
            parameter/parameter already there.

        + add_input
            Add input to the task(with alias), print something, maybe changed later.
        + remove_input
            Remove input of the task through alias.

        + add_algorithm
            Add the algorithm correspnding to the task. if already has algorithm, replace the
            old one and print the message. Maybe changed later because I do not want to print
            anything in the kernel.
        + remove_algorithm
            Remove the algorithm corresponding to the task. if nothing to remove it print the
            message. Maybe changed later because I do not want to print anything in the kernel.
        + algorithm
            Return the algorithm corresponding to this task. If the task is not related to an
            algorithm, return None.

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
from logging import getLogger
from os.path import join

from ..utils import utils
from ..utils import metadata
from ..utils import csys
from ..utils.pretty import colorize

from .chern_cache import ChernCache
from .ChernCommunicator import ChernCommunicator

from .VObject import VObject
from .vtask_input import InputManager
from .vtask_setting import SettingManager
from .vtask_core import Core
from .vtask_file import FileManager
from .vtask_job import JobManager

CHERN_CACHE = ChernCache.instance()
logger = getLogger("ChernLogger")


class VTask(VObject, Core, InputManager, SettingManager, FileManager, JobManager):
    """ The main vtask class
    It contains: Core, InputManager, SettingManager, FileManager, JobManager
    """
    def output_files(self):
        """ [unused]
        """
        return []

    def get_file(self, filename):
        """ Get file from ChernCommunicator
        """
        cherncc = ChernCommunicator.instance()
        return cherncc.get_file("local", self.impression(), filename)

    def view(self, filename):
        """ View the file through ChernCommunicator
        """
        if filename.startswith("local:"):
            path = self.get_file("local:" + filename[6:])
            if not csys.exists(path):
                print(f"File: {path} do not exists")
                return
            with open_subprocess(f"open {path}") as process:
                pass

    def print_status(self):
        """ Print the status of the task
        """
        print(f"Status of task: {self.invariant_path()}")
        if self.status() == "impressed":
            print(f"Impression: [{colorize(self.impression().uuid, 'success')}]")
        else:
            print(f"Impression: [{colorize('New', 'warning')}]")
            return
        cherncc = ChernCommunicator.instance()
        dite_status = cherncc.dite_status()
        if dite_status == "ok":
            print(f"DIET: [{colorize('connected', 'success')}]")
        else:
            print(f"DIET: [{colorize('unconnected', 'warning')}]")
            return

        deposited = cherncc.is_deposited(self.impression())
        if deposited == "FALSE":
            print("Impression not deposited in DIET")
            return

        job_status = cherncc.job_status(self.impression())
        print(f"Job status: [{colorize(job_status, 'success')}]")

        environment = self.environment()
        if environment == "rawdata":
            run_status = self.run_status()
            print(f"Sample status: [{colorize(run_status, run_status)}]")
            files = cherncc.output_files(self.impression(), "none")
            print("Sample files (collected on DIET):")
            for f in files:
                print("    {f}")
            return

        workflow_check = cherncc.workflow(self.impression())
        if workflow_check[0] == "UNDEFINED":
            print("Workflow not defined")
            return

        if environment != "rawdata":
            print(colorize("**** WORKFLOW:", "title0"))
            runner = workflow_check[0]
            workflow = workflow_check[1]
            print(f"Workflow: [{colorize(runner,'success')}][{colorize(workflow, 'success')}]")

            files = cherncc.output_files(self.impression(), runner)
            print("Output files (collected on DIET):")
            for f in files:
                print(f"    {f}")

    def status(self, consult_id=None):
        """ Consult the status of the object
            There should be only two status locally: new|impressed
        """
        # If it is already asked, just give us the answer
        logger.debug("VTask status: Consulting status of %s", self.path)
        if consult_id:
            consult_table = CHERN_CACHE.status_consult_table
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
    """ Create a task
    """
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(join(path, ".."))
    object_type = VObject(parent_path).object_type()
    if object_type not in ("project", "directory"):
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

    with open(path + "/.chern/README.md", "w", encoding="utf-8") as f:
        f.write(f"Please write README for task {task.invariant_path()}")


def create_data(path):
    """ Create a data
    """
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(path+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type not in ("project", "directory"):
        return

    csys.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path + "/.chern/config.json")
    config_file.write_variable("object_type", "task")
    task = VObject(path)

    with open(path + "/.chern/README.md", "w", encoding="utf-8") as f:
        f.write(f"Please write README for task {task.invariant_path()}")

    yaml_file = metadata.YamlFile(join(path, "chern.yaml"))
    yaml_file.write_variable("environment", "rawdata")
    yaml_file.write_variable("uuid", "")
