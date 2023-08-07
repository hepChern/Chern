""" VAlgorithm
"""
import uuid
import time
import os
import subprocess

from Chern.kernel.VObject import VObject
# from Chern.kernel.VImage import VImage
# from Chern.kernel.ChernDatabase import ChernDatabase
from Chern.kernel.ChernCache import ChernCache

from Chern.utils import utils
from Chern.utils import csys
from Chern.utils.utils import color_print
from Chern.utils import git
from Chern.utils.utils import colorize
from Chern.utils import metadata

from Chern.kernel.ChernCommunicator import ChernCommunicator
cherncache = ChernCache.instance()

class VAlgorithm(VObject):
    """ Algorithm class
    """

    def helpme(self, command):
        from Chern.kernel.Helpme import algorithm_helpme
        print(algorithm_helpme.get(command, "No such command, try ``helpme'' alone."))

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
        
    """
    def jobs(self):
        impressions = self.config_file.read_variable("impressions", [])
        if impressions == []:
            return
        impression = self.config_file.read_variable("impression")
        for im in impressions:
            path = utils.storage_path() + "/" + im
            if not os.path.exists(path):
                continue
            if impression == im:
                short = "*"
            else:
                short = " "
            short += im[:8]
            status = VImage(path).status()
            print("{0:<12}   {1:>20}".format(short, status))
    """

    def is_submitted(self):
        """ Judge whether submitted or not. Return a True or False.
        [FIXME: incomplete]
        """
        if not self.is_impressed_fast():
            return False
        return False

    """
    def submit(self):
        if self.is_submitted():
            return ["[ERROR] {0} already submitted! Skip ``submit''.".format(self.invariant_path())]
        if not self.is_impressed_fast():
            self.impress()

        path = csys.storage_path() + "/" + self.impression()
        cwd = self.path
        utils.copy_tree(cwd, path)
        image = self.image()
        image.config_file.write_variable("job_type", "image")
        cherndb.add_job(self.impression())
    """


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

    """
    def image(self):
        # Get the image. If the image is not exists raise a exception.
        path = utils.storage_path() + "/" + self.impression()
        if not os.path.exists(path):
            raise Exception("Image does not exist.")
        return VImage(path)
    """

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
