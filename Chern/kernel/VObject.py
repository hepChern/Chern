import os
import shutil
import time
from Chern.utils import utils
from Chern.utils.utils import debug
from Chern.utils.utils import colorize
from Chern.utils.utils import color_print
from Chern.kernel.ChernDaemon import status as daemon_status
from subprocess import call
import subprocess
from Chern.utils import git
from Chern.kernel.ChernDatabase import ChernDatabase

cherndb = ChernDatabase.instance()

class VObject(object):
    """ Virtual class of the objects, including VData, VAlgorithm, VData and VDirectory
    """

    def __init__(self, path):
        """ Initialize a instance of the object.
        All the infomation is directly read from and write to the disk.
        """
        self.path = utils.strip_path_string(path)
        self.created_time = time.time()
        self.config_file = utils.ConfigFile(self.path+"/.chern/config.py")

    def invariant_path(self):
        """ The path relative to the project root.
        It is invariant when the project is moved.
        """
        project_path = cherndb.project_path()
        path = os.path.relpath(self.path, project_path)
        return path

    def __str__(self):
        """ Define the behavior of print(vobject)
        """
        return self.invariant_path()

    def __repr__(self):
        """ Define the behavior of print(vobject)
        """
        return self.invariant_path()

    def is_git_committed(self, is_global=False):
        """ Whether the object is recorded by git.
        FIXME: the is_global flag maybe useless.
        """
        if is_global:
            ps = subprocess.Popen("git status", shell=True, stdout=subprocess.PIPE)
        else:
            ps = subprocess.Popen("git status -- {0}".format(self.path), shell=True, stdout=subprocess.PIPE)
        ps.wait()
        output = ps.stdout.read()
        return output.decode().find("nothing to commit") != -1

    def relative_path(self, path):
        """ Return a path relative to the path of this object
        """
        return os.path.relpath(path, self.path)

    def is_modified(self):
        """ FIXME: may be replaced by the git commit method.
        Return whether this object object is modified.
        Check should be done before every use.
        """
        return False

    def object_type(self, path=None):
        """
        Return the type of the object under a specific path.
        If path is left blank, return the type of the object itself.
        """
        if path is None:
            path = self.path
        # simply read object_type in .chern/config.py
        config_file = utils.ConfigFile(path+"/.chern/config.py")
        return config_file.read_variable("object_type")

    def ls(self):
        """
        FIXME
        Print the subdirectory of the object
        I recommend to print also the README
        and the parameters|inputs|outputs ...
        And it's better to give a number to the listed
        object and therefore, command like cd 1
        can be used
        """
        if not cherndb.is_docker_started():
            color_print("!!Warning: docker not started", color="warning")
        if daemon_status() != "started":
            color_print("!!Warning: runner not started {}".format(daemon_status()), color="warning")
        print(colorize("README:", "comment"))
        print(colorize(self.readme(), "comment"))
        sub_objects = self.sub_objects()
        sub_objects.sort(key=lambda x:(x.object_type(),x.path))
        if sub_objects:
            print(colorize(">>>> Subobjects:", "title0"))
        for index, sub_object in enumerate(sub_objects):
            print("{2} {0:<12} {1:>20}".format("("+sub_object.object_type()+")", self.relative_path(sub_object.path), "[{}]".format(index)))
        total = len(sub_objects)
        predecessors = self.predecessors()
        if predecessors:
            print(colorize("o--> Predecessors:", "title0"))
        for index, pred_object in enumerate(predecessors):
            alias = self.path_to_alias(pred_object.invariant_path())
            order = "[{}]".format(total+index)
            pred_path = pred_object.invariant_path()
            obj_type = "("+pred_object.object_type()+")"
            print("{2} {0:<12} {3:>10}: {1:<20}".format(obj_type, pred_path, order, alias))
        total += len(predecessors)
        successors = self.successors()
        if successors:
            print(colorize("-->o Successors:", "title0"))
        for index, succ_object in enumerate(successors):
            alias = self.path_to_alias(succ_object.invariant_path())
            order = "[{}]".format(total+index)
            succ_path = succ_object.invariant_path()
            obj_type = "("+succ_object.object_type()+")"
            print("{2} {0:<12} {3:>10}: {1:<20}".format(obj_type, succ_path, order, alias))

    def add_arc_from(self, path):
        """ Add an link from the object contains in `path' to this object.
        FIXME: it directly operate the config_file of other object rather operate through.
        """
        config_file = utils.ConfigFile(path+"/.chern/config.py")
        succ_str = config_file.read_variable("successors")
        if succ_str is None:
            succ_str = []
        succ_str.append(self.invariant_path())
        config_file.write_variable("successors", succ_str)

        pred_str = self.config_file.read_variable("predecessors")
        if pred_str is None:
            pred_str = []
        pred_str.append(VObject(path).invariant_path())
        self.config_file.write_variable("predecessors", pred_str)

    def remove_arc_from(self, path):
        """
        FIXME
        Remove link from the path
        Just copied from "remove_arc_from"
        """
        config_file = utils.ConfigFile(path+"/.chern/config.py")
        succ_str = config_file.read_variable("successors")
        succ_str.remove(self.invariant_path())
        config_file.write_variable("successors", succ_str)
        config_file = utils.ConfigFile(self.path+"/.chern/config.py")
        pred_str = config_file.read_variable("predecessors")
        pred_str.remove(VObject(path).invariant_path())
        config_file.write_variable("predecessors", pred_str)

    def add_arc_to(self, path):
        """
        FIXME
        Add a link from this object to the path object
        """
        config_file = utils.ConfigFile(path+"/.chern/config.py")
        pred_str = config_file.read_variable("predecessors")
        if pred_str is None:
            pred_str = []
        pred_str.append(self.path)
        config_file.write_variable("predecessors", pred_str)
        config_file = utils.ConfigFile(self.path+"/.chern/config.py")
        succ_str = config_file.read_variable("successors")
        if succ_str is None:
            succ_str = []
        succ_str.append(path)
        config_file.write_variable("successors", succ_str)

    def remove_arc_to(self, path):
        """
        FIXME
        remove the path to the path
        """
        config_file = utils.ConfigFile(path+"/.chern/config.py")
        pred_str = config_file.read_variable("predecessors")
        pred_str.remove(self.path)
        config_file.write_variable("predecessors", pred_str)
        config_file = utils.ConfigFile(self.path+"/.chern/config.py")
        succ_str = config_file.read_variable("successors")
        succ_str.remove(path)
        config_file.write_variable("successors", succ_str)

    def successors(self):
        """
        The successors of the current object
        """
        succ_str = self.config_file.read_variable("successors")
        if succ_str is None:
            return []
        successors = []
        project_path = cherndb.project_path()
        for path in succ_str:
            successors.append(VObject(project_path+"/"+path))
        return successors

    def predecessors(self):
        pred_str = self.config_file.read_variable("predecessors")
        if pred_str is None:
            return []
        predecessors = []
        project_path = cherndb.project_path()
        for path in pred_str:
            predecessors.append(VObject(project_path+"/"+path))
        return predecessors

    def cp(self, new_path):
        """
        FIXME
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            new_object = VObject(new_path +"/"+ self.relative_path(obj.path))

    def path_to_alias(self, path):
        path_to_alias = self.config_file.read_variable("path_to_alias")
        if path_to_alias is None:
            return ""
        return path_to_alias.get(path, "")

    def alias_to_path(self, alias):
        alias_to_path = self.config_file.read_variable("alias_to_path")
        return alias_to_path[alias]

    def remove_alias(self, alias):
        if alias == "":
            return
        alias_to_path = self.config_file.read_variable("alias_to_path")
        path_to_alias = self.config_file.read_variable("path_to_alias")
        path = alias_to_path[alias]
        path_to_alias.pop(path)
        alias_to_path.pop(alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)
        self.config_file.write_variable("path_to_alias", path_to_alias)

    def set_alias(self, alias, path):
        if alias == "":
            return
        path_to_alias = self.config_file.read_variable("path_to_alias")
        alias_to_path = self.config_file.read_variable("alias_to_path")
        if path_to_alias is None:
            path_to_alias = {}
        if alias_to_path is None:
            alias_to_path = {}
        path_to_alias[path] = alias
        alias_to_path[alias] = path
        self.config_file.write_variable("path_to_alias", path_to_alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)

    def clean(self):
        """
        Clean all the alias, predecessors and successors
        """
        self.config_file.write_variable("alias_to_path", {})
        self.config_file.write_variable("path_to_alias", {})
        self.config_file.write_variable("predecessors", [])
        self.config_file.write_variable("successors", [])

    def mv(self, new_path):
        """
        FIXME
        mv to another path
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))
            new_object = VObject(norm_path)
            new_object.clean()
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    new_object.add_arc_from(pred_object.path)
                    alias1 = obj.path_to_alias(pred_object.path)
                    alias2 = pred_object.path_to_alias(obj.path)
                    new_object.set_alias(alias1, pred_object.invariant_path())
                    pred_object.remove_alias(alias2)
                    pred_object.set_alias(alias2, new_object.invariant_path())
                else:
                # if in the same tree
                    relative_path = self.relative_path(pred_object.path)
                    new_object.add_arc_from(new_path+"/"+relative_path)
                    alias1 = obj.path_to_alias(pred_object.path)
                    alias2 = pred_object.path_to_alias(obj.path)
                    norm_path = os.path.normpath(new_path +"/"+ relative_path)
                    new_object.set_alias(alias1, VObject(norm_path).invariant_path())
                    VObject(norm_path).set_alias(alias2, new_object.invariant_path())
            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    new_object.add_arc_to(succ_object.path)
                    alias1 = obj.path_to_alias(succ_object.path)
                    alias2 = succ_object.path_to_alias(obj.path)
                    new_object.set_alias(alias1, succ_object.invariant_path())
                    succ_object.remove_alias(alias2)
                    succ_object.set_alias(alias2, new_object.invariant_path())
        for obj in queue:
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    obj.remove_arc_from(pred_object.path)
            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    obj.remove_arc_to(succ_object.path)

    def add(self, src, dst):
        if not os.path.exists(src):
            return
        utils.copy(src, self.path+"/"+dst)
        git.add(self.path+"/"+dst)
        git.commit("Add {}".format(dst))

    def rm(self):
        """
        Remove this object.
        The important this is to unalias
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    obj.remove_arc_from(pred_object.path)
                    alias = pred_object.path_to_alias(pred_object.path)
                    pred_object.remove_alias(alias)
            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    obj.remove_arc_to(succ_object.path)
                    alias = succ_object.path_to_alias(succ_object.path)
                    succ_object.remove_alias(alias)
        shutil.rmtree(self.path)
        git.rm(self.path)
        git.commit("rm {}".format(self.invariant_path()))

    def sub_objects(self):
        """ return a list of the sub_objects
        """
        sub_directories = os.listdir(self.path)
        sub_object_list = []
        for item in sub_directories:
            if os.path.isdir(self.path+"/"+item):
                object_type = self.object_type(self.path+"/"+item)
                if object_type is None:
                    continue
                sub_object_list.append(VObject(self.path+"/"+item))
        return sub_object_list

    def sub_objects_recursively(self):
        """
        Return a list of all the sub_objects
        """
        queue = [self]
        index = 0
        while index < len(queue):
            top_object = queue[index]
            queue += top_object.sub_objects()
            index += 1
        return queue

    def latest_commit_message(self, is_global=False):
        if is_global:
            log = git.log('-n 1 --format="%s"').split("\n")
        else:
            log = git.log('-n 1 --format="%s" -- {}'.format(self.path)).split("\n")
        return log[0]

    def edit_readme(self):
        """
        FIXME
        need more editor support
        """
        call("vim {0}".format(self.path+"/README.md"), shell=True)
        git.add(self.path+"/README.md")
        message = self.latest_commit_message()
        git.commit("{} + edit readme".format(message))

    def impression(self):
        impression = self.config_file.read_variable("impression")
        return impression

    def readme(self):
        """
        FIXME
        Get the README String.
        I'd like it to support more
        """
        with open(self.path+"/README.md") as f:
            return f.read().strip("\n")

    def __getitem__(self, index):
        """
        FIXME
        This method should be written to realize the function like
        a.b.c
        """
        pass