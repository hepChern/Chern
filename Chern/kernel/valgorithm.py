""" VAlgorithm
"""
import os
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
        print(f"Status of task: {self.invariant_path()}")
        if self.status() == "impressed":
            print(f"Impression: [{colorize(self.impression().uuid, 'success')}]")
        else:
            print(f"Impression: [{colorize('New','warning')}]")
            return
        cherncc = ChernCommunicator.instance()
        dite_status = cherncc.dite_status()
        if dite_status == "ok":
            print(f"DIET: [{colorize('connected','success')}]")
        else:
            print(f"DIET: [{colorize('unconnected','warning')}]")
            return

        deposited = cherncc.is_deposited(self.impression())
        if deposited == "FALSE":
            print("Impression not deposited in DIET")
            return

        environment = self.environment()

        workflow_check = cherncc.workflow(self.impression())
        if workflow_check == "UNDEFINED":
            print("Workflow not defined")
            return

        if environment != "rawdata":
            print(colorize("**** WORKFLOW:", "title0"))
            runner = workflow_check[0]
            workflow = workflow_check[1]
            print(f"Workflow: [{colorize(runner,'success')}][{colorize(workflow,'success')}]")

            files = cherncc.output_files(self.impression(), runner)
            print("Output files (collected on DIET):")
            for f in files:
                print(f"    {f}")

    def job_status(self):
        """ Asking for the remote status
        """
        cherncc = ChernCommunicator.instance()
        return cherncc.job_status(self.impression())

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


        print(colorize("---- Files:", "title0"))
        files = os.listdir(self.path)
        for f in files:
            if not f.startswith(".") and f != "README.md":
                print(f)

    def commands(self):
        """ Get the commands from the yaml file """
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        return yaml_file.read_variable("commands", [])

    def importfile(self, file):
        """
        Import the file to this task directory
        """
        if not os.path.exists(file):
            print("File does not exist.")
            return
        filename = os.path.basename(file)
        if os.path.exists(self.path + "/" + filename):
            print("File already exists.")
            return
        csys.copy_tree(file, self.path + "/" + filename)

    def environment(self):
        """ Get the environment
        """
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        return yaml_file.read_variable("environment", {})

    def remove_input(self, alias):
        """ Remove the input """
        path = self.alias_to_path(alias)
        if path == "":
            print("Alias not found")
            return
        project_path = csys.project_path(self.path)
        obj = VObject(project_path+"/"+path)
        self.remove_arc_from(obj)
        self.remove_alias(alias)

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
