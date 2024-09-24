""" The VDirectory class
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    VDirectory:
    #Methods:
        + helpme:
            Print the helpme of this directory
            FIXME: Maybe transfer to return the helpme and putting the
            printing function to interface
        + status:
            Give the status of the object
        + submit:
            Submit the contents of the directory(apply submit to the tasks/algorithms/subdirectories)
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
import Chern
from Chern.utils import utils
from Chern.utils import csys
from Chern.utils import metadata
from Chern.kernel.VObject import VObject
from Chern.kernel.ChernCommunicator import ChernCommunicator
class VDirectory(VObject):
    """
    Nothing more to do for this VDirectory.
    """
    def helpme(self, command):
        from Chern.kernel.Helpme import directory_helpme
        print(directory_helpme.get(command, "No such command, try ``helpme'' alone."))

    def status(self, consult_id = None):
        sub_objects = self.sub_objects()
        for sub_object in sub_objects:
            if sub_object.object_type() == "task":
                status = Chern.kernel.VTask.VTask(sub_object.path).status(consult_id)
                if status == "running":
                    return "processing"
            elif sub_object.object_type() == "algorithm":
                if Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).status(consult_id) == "building":
                    return "processing"
            else:
                status = Chern.kernel.VDirectory.VDirectory(sub_object.path).status(consult_id)
                if status == "processing":
                    return "processing"

        for sub_object in sub_objects:
            if sub_object.object_type() == "task":
                status = Chern.kernel.VTask.VTask(sub_object.path).status(consult_id)
                if status != "done":
                    return "unfinished"
            elif sub_object.object_type() == "algorithm":
                if Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).status(consult_id) != "built":
                    return "unfinished"
            else:
                status = Chern.kernel.VDirectory.VDirectory(sub_object.path).status(consult_id)
                if status != "finished":
                    return "unfinished"

        return "finished"

    def get_impressions(self):
        impressions = []
        sub_objects = self.sub_objects()
        for sub_object in sub_objects:
            if sub_object.object_type() == "task" or sub_object.object_type() == "algorithm":
                impressions.append(sub_object.impression().uuid)
            else:
                sub_object = Chern.kernel.VDirectory.VDirectory(sub_object.path)
                impressions.extend(sub_object.get_impressions())
        return impressions

    def deposit(self, machine = "local"):
        sub_objects = self.sub_objects()
        for sub_object in sub_objects:
            if sub_object.object_type() == "task":
                Chern.kernel.VTask.VTask(sub_object.path).deposit()
            elif sub_object.object_type() == "algorithm":
                Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).deposit()
            else:
                Chern.kernel.VDirectory.VDirectory(sub_object.path).deposit()

    def submit(self, machine = "local"):
        cherncc = ChernCommunicator.instance()
        self.deposit(machine)
        impressions = self.get_impressions()
        cherncc.execute(impressions, machine)

    def print_status(self):
        return
        # FIXME: This function is not used now
        print("Status of directory: {}".format(self.invariant_path()))
        cherncc = ChernCommunicator.instance()
        host_status = cherncc.host_status()
        if host_status == "ok":
            print("    Host: [{}]".format(colorize("Online", "success")))

        for sub_object in self.sub_objects():
            if sub_object.object_type() == "task" or sub_object.object_type() == "algorithm":
                print("    Task: {}".format(sub_object.invariant_path()))
                task = Chern.kernel.VTask.VTask(sub_object.path)
                if task.status() == "impressed":
                    print("Impression: [{}]".format(colorize(task.impression().uuid, "success")))
                else:
                    print("Impression: [{}]".format(colorize("New", "normal")))
                    continue
            if host_status == "ok":
                if sub_object.object_type() == "task":
                    status = Chern.kernel.VTask.VTask(sub_object.path).status()
                elif sub_object.object_type() == "algorithm":
                    status = Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).status()
                else:
                    status = Chern.kernel.VDirectory.VDirectory(sub_object.path).status()
                print("    Status: [{}]".format(colorize(status, "success")))


    def clean_impressions(self):
        sub_objects = self.sub_objects()
        for sub_object in sub_objects:
            if sub_object.object_type() == "task":
                Chern.kernel.VTask.VTask(sub_object.path).clean_impressions()
            elif sub_object.object_type() == "algorithm":
                Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).clean_impressions()
            else:
                Chern.kernel.VDirectory.VDirectory(sub_object.path).clean_impressions()

def create_directory(path, inloop=False):
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(path+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "project" and object_type != "directory":
        raise Exception("create directory only under project or directory")
    csys.mkdir(path)
    csys.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path + "/.chern/config.json")
    config_file.write_variable("object_type", "directory")
    directory = VObject(path)

    with open(path + "/.chern/README.md", "w") as f:
        f.write("Please write README for the directory {}".format(directory.invariant_path()))
