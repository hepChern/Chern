""" VAlgorithm
"""
import os
import subprocess

from .VObject import VObject
from .chern_cache import ChernCache

from ..utils import utils
from ..utils import csys
from ..utils.pretty import colorize
from ..utils import metadata

from .ChernCommunicator import ChernCommunicator
cherncache = ChernCache.instance()


class VAlgorithm(VObject):
    """ Algorithm class
    """

    def helpme(self, command):
        from Chern.kernel.Helpme import algorithm_helpme
        print(algorithm_helpme.get(command, "No such command, try ``helpme'' alone."))


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


    def status(self, consult_id = None, detailed = False):
        """ Consult the status of the object
            There should be only two status locally: new|impressed
        """
        # If it is already asked, just give us the answer
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



    def run_status(self, consult_id = None):
        """ Asking for the remote status
        """
        cherncc = ChernCommunicator.instance()
        return cherncc.status(self.impression())

    def is_submitted(self):
        """ Judge whether submitted or not. Return a True or False.
        [FIXME: incomplete]
        """
        if not self.is_impressed_fast():
            return False
        return False

    def resubmit(self):
        if not self.is_submitted():
            print("Not submitted yet.")
            return
        path = utils.storage_path() + "/" + self.impression()
        csys.rm_tree(path)
        self.submit()

    def stdout(self):
        """ stdout
        """
        with open(self.image().path+"/stdout") as stdout_file:
            return stdout_file.read()

    def stderr(self):
        """ Std error
        """
        with open(self.image().path+"/stderr") as stderr_file:
            return stderr_file.read()

    def ls(self, show_readme=True, show_predecessors=True, show_sub_objects=True, show_status=True, show_successors=False):
        """ list the infomation.
        """
        super(VAlgorithm, self).ls(show_readme, show_predecessors, show_sub_objects, show_status, show_successors)

        if show_status:
            status = self.status()
            if status == "new":
                status_color = "normal"
            elif status == "impressed":
                status_color = "success"

            status_str = colorize("["+status+"]", status_color)

            if status == "impressed":
                run_status = self.run_status()
                if run_status != "unconnected":
                    if (run_status == "unsubmitted"):
                        status_color = "warning"
                    elif (run_status == "failed"):
                        status_color = "warning"
                    else:
                        status_color = "success"
                        status_str += colorize("["+run_status+"]", status_color)
            print(colorize("**** STATUS:", "title0"), status_str)

        if self.is_submitted() and self.image().error() != "":
            print(colorize("!!!! ERROR:\n", "title0"), self.image().error())

        print(colorize("---- Files:", "title0"))
        files = os.listdir(self.path)
        for f in files:
            if not f.startswith(".") and f != "README.md":
                print(f)

    def commands(self):
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

    def add_input(self, path, alias):
        """ FIXME: judge the input type
        """
        obj = VObject(path)
        if obj.object_type() != "algorithm":
            print("You are adding {} type object as input. The input is required to be an algorithm.".format(obj.object_type()))
            return

        if obj.has_predecessor_recursively(self):
            print("The object is already in the dependency diagram of the ``input'', which will cause a loop.")
            return

        if self.has_alias(alias):
            print("The alias already exists. The original input and alias will be replaced.")
            project_path = csys.project_path(self.path)
            original_object = VObject(project_path+"/"+self.alias_to_path(alias))
            self.remove_arc_from(original_object)
            self.remove_alias(alias)

        self.add_arc_from(obj)
        self.set_alias(alias, obj.invariant_path())

    def remove_input(self, alias):
        path = self.alias_to_path(alias)
        if path == "":
            print("Alias not found")
            return
        project_path = csys.project_path(self.path)
        obj = VObject(project_path+"/"+path)
        self.remove_arc_from()
        self.remove_alias(alias)

    def importfile(self, filename):
        """
        Import the file to this task directory
        """
        csys.copy(filename, self.path)






def create_algorithm(path, use_template=False):
    path = utils.strip_path_string(path)
    os.mkdir(path)
    os.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path+"/.chern/config.json")
    config_file.write_variable("object_type", "algorithm")

    with open(path + "/.chern/README.md", "w") as readme_file:
        readme_file.write("Please write README for this algorithm")
    subprocess.call("vim {}/.chern/README.md".format(path), shell=True)
    if use_template:
        template_name = input("Please input the Dockerfile template type")
        print("Creating template, but hahahaha")
        return
