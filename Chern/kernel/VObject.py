""" Virtual base class for all ```directory'', ``task'', ``algorithm''
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    VObject:
    #Methods:
        + __init__:
            It should be initialized with a absolute path. The initialization gets variable "path" and "config_file".
            It is quite light-weight to create a VObject. A VObject can be abandoned after using and create another when needed.

        + __str__, __repr__:
            For print

        + invariant_path:
            Return the path relative to the project root
        + relative_path(a_path);
            Return the path of the VObject relative to a_path

        + object_type:
            Return the type of the object: project, task, directory, or empty("")
        + is_zombine
            To judge whether this object has a type

        + color_tag: (Maybe put it somewhere else?)
            For print

        + ls:
            Realization of "ls" call o.ls() will give you the contents of the object

        + add_arc_from(obj)
        + remove_arc_from(obj, single=False)
        + add_arc_to(obj)
        + remove_arc_from(obj, single=False):
            Add or remove arcs, the "single" variable is only used for debug usage.

        + successors
        + predecessors:
            Get [objects]
        + has_successor(obj)
        + has_predessor(obj)
            Judge whether obj is the succ/pred of this obj

        + doctor:
            Judge whether it is a good object(with all arc linked)

        + copy_to:
            Copy the object and its contains to a new path. Before the copy, all objects in the directory will be impressed.
            The arcs within the directory will be kept and outsides will be removed.
        + clean_impressions
        + clean_flow:
            Helpers for copy_to

        + path_to_alias
        + alias_to_path
        + has_alias
        + set_alias
        + remove_alias

        + move_to:
            Move the object to another directory

        + rm:
            Remove the object

        + impression:
            Return the impression of the object
        + impress:
            Make a impression
        + is_impressed:
            Judge whether this object is impressed

        + pack_impression:
        + unpack_impression:
        + is_packed:
            For future transfer purpose
"""
import os
import shutil
import time
import subprocess
import Chern
import uuid
import filecmp
from Chern.utils import csys
from Chern.utils import metadata
from Chern.utils.pretty import colorize
from Chern.utils.utils import color_print

from Chern.kernel.VImpression import VImpression
from Chern.kernel.ChernCache import ChernCache
from Chern.kernel.ChernCommunicator import ChernCommunicator

import logging
from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")

class VObject(object):
    """ Virtual class of the objects, including VData, VAlgorithm and VDirectory
    """

    def __init__(self, path):
        """ Initialize a instance of the object.
        All the information is directly read from and write to the disk.
        parameter ``path'' is allowed to be a string begin with empty characters.
        """
        logger.debug("VObject init: {}".format(path))
        self.path = csys.strip_path_string(path)
        self.config_file = metadata.ConfigFile(self.path+"/.chern/config.json")
        logger.debug("VObject init done: {}".format(path))


    def __str__(self):
        """ Define the behavior of print(vobject)
        """
        return self.invariant_path()

    def __repr__(self):
        """ Define the behavior of print(vobject)
        """
        return self.invariant_path()

    def invariant_path(self):
        """ The path relative to the project root.
        It is invariant when the project is moved.
        """
        project_path = csys.project_path(self.path)
        path = os.path.relpath(self.path, project_path)
        return path

    def relative_path(self, path):
        """ Return a path relative to the path of this object
        """
        return os.path.relpath(path, self.path)

    def object_type(self):
        """ Return the type of the this object.
        """
        return self.config_file.read_variable("object_type", "")

    def is_zombie(self):
        """ Judge whether it is actually an object
        """
        return self.object_type() == ""

    def color_tag(self, status):
        """ Get the color tag according to the status.
        """
        if status == "built" or status == "done" or status == "finished":
            color_tag = "success"
        elif status == "failed" or status == "unfinished":
            color_tag = "warning"
        elif status == "running":
            color_tag = "running"
        else:
            color_tag = "normal"
        return color_tag

    def ls(self, show_readme=True, show_predecessors=True, show_sub_objects=True, show_status=False, show_successors=False):
        """ Print the subdirectory of the object
        I recommend to print also the README
        and the parameters|inputs|outputs ...
        """

        """
        FIXME: Should communicate with ChernCommunicator to get the runner status
        if not cherncache.is_docker_started():
            color_print("!!Warning: docker not started", color="warning")
        if daemon_status() != "started":
            color_print("!!Warning: runner not started, the status is {}".format(daemon_status()), color="warning")
        """

        logger.debug("VObject ls: {}".format(self.invariant_path()))
        cherncc = ChernCommunicator.instance()

        # Should have a flag whether to show the runner
        """
        hosts = cherncc.hosts()
        hosts_status = colorize(">>>> Runners connection : ", "title0")
        for host in hosts:
            status = cherncc.host_status(host)
            if (status == "ok"):
                hosts_status += colorize("["+host+"] ", "success")
            elif (status == "unconnected"):
                hosts_status += colorize("["+host+"] ", "warning")
        print(hosts_status)
        """
        hosts_status = colorize(">>>> DITE: ", "title0")
        status = cherncc.host_status()
        if (status == "ok"):
            hosts_status += colorize("[connected] ", "success")
        elif (status == "unconnected"):
            hosts_status += colorize("[unconnected] ", "warning")
        print(hosts_status)

        if show_readme:
            print(colorize("README:", "comment"))
            print(colorize(self.readme(), "comment"))

        sub_objects = self.sub_objects()
        sub_objects.sort(key=lambda x:(x.object_type(),x.path))
        if sub_objects and show_sub_objects:
            print(colorize(">>>> Subobjects:", "title0"))

        if show_sub_objects:
            for index, sub_object in enumerate(sub_objects):
                sub_path = self.relative_path(sub_object.path)
                if show_status:
                    status = Chern.interface.ChernManager.create_object_instance(sub_object.path).status()
                    color_tag = self.color_tag(status)
                    print("{2} {0:<12} {1:>20} ({3})".format("("+sub_object.object_type()+")", sub_path, "[{}]".format(index), colorize(status, color_tag)))
                else:
                    print("{2} {0:<12} {1:>20}".format("("+sub_object.object_type()+")", sub_path, "[{}]".format(index)))

        total = len(sub_objects)
        predecessors = self.predecessors()
        if predecessors and show_predecessors:
            print(colorize("o--> Predecessors:", "title0"))
            for index, pred_object in enumerate(predecessors):
                alias = self.path_to_alias(pred_object.invariant_path())
                order = "[{}]".format(total+index)
                pred_path = pred_object.invariant_path()
                obj_type = "("+pred_object.object_type()+")"
                print("{2} {0:<12} {3:>10}: @/{1:<20}".format(obj_type, pred_path, order, alias))

        total += len(predecessors)
        successors = self.successors()
        if successors and show_successors:
            print(colorize("-->o Successors:", "title0"))
            for index, succ_object in enumerate(successors):
                alias = self.path_to_alias(succ_object.invariant_path())
                order = "[{}]".format(total+index)
                succ_path = succ_object.invariant_path()
                obj_type = "("+succ_object.object_type()+")"
                print("{2} {0:<12} {3:>10}: @/{1:<20}".format(obj_type, succ_path, order, alias))

    def add_arc_from(self, obj):
        """ Add an link from the object contains in `path' to this object.
         o  --*--> (o) ----> o.
        (o) --*-->  o         .
        """
        succ_str = obj.config_file.read_variable("successors", [])
        succ_str.append(self.invariant_path())
        obj.config_file.write_variable("successors", succ_str)

        pred_str = self.config_file.read_variable("predecessors", [])
        pred_str.append(obj.invariant_path())
        self.config_file.write_variable("predecessors", pred_str)

    def remove_arc_from(self, obj, single=False):
        """ Remove link from the path
        If ``single'' is set to be True, we will only remove the arc in this object.
         o  --X--> (o) ----> o. Remove this arc.
        (o) --X-->  o         . If single set to False, this arc is removed.
        """
        if not single:
            config_file = obj.config_file
            succ_str = config_file.read_variable("successors", [])
            succ_str.remove(self.invariant_path())
            config_file.write_variable("successors", succ_str)

        pred_str = self.config_file.read_variable("predecessors", [])
        pred_str.remove(obj.invariant_path())
        self.config_file.write_variable("predecessors", pred_str)

    def add_arc_to(self, obj):
        """ Add a link from this object to the path object
         o  -----> (o) --*-->  o .
                    o  --*--> (o).
        """
        pred_str = obj.config_file.read_variable("predecessors", [])
        pred_str.append(self.invariant_path())
        obj.config_file.write_variable("predecessors", pred_str)

        succ_str = self.config_file.read_variable("successors", [])
        succ_str.append(obj.invariant_path())
        self.config_file.write_variable("successors", succ_str)

    def remove_arc_to(self, obj, single=False):
        """ remove the path to the path
         o  -----> (o) --X-->  o .  Remove this arc.
                    o  --X--> (o).  If single set to False, this arc is removed.
        """
        if not single:
            config_file = obj.config_file
            pred_str = config_file.read_variable("predecessors", [])
            pred_str.remove(self.invariant_path())
            config_file.write_variable("predecessors", pred_str)

        succ_str = self.config_file.read_variable("successors", [])
        succ_str.remove(obj.invariant_path())
        self.config_file.write_variable("successors", succ_str)

    def successors(self):
        """ The successors of the current object
        Return a list of [object]
        """
        succ_str = self.config_file.read_variable("successors", [])
        successors = []
        project_path = csys.project_path(self.path)
        for path in succ_str:
            successors.append(VObject(project_path+"/"+path))
        return successors

    def predecessors(self):
        """ The predecessosr of the current object
        Return a list of [object]
        """
        pred_str = self.config_file.read_variable("predecessors", [])
        predecessors = []
        project_path = csys.project_path(self.path)
        for path in pred_str:
            predecessors.append(VObject(project_path+"/"+path))
        return predecessors

    def has_successor(self, obj):
        """ Judge whether the object has the specific successor
        """
        succ_str = self.config_file.read_variable("successors", [])
        return obj.invariant_path() in succ_str

    def has_predecessor(self, obj):
        """ Judge whether the object has the specific predecessor
        """
        pred_str = self.config_file.read_variable("predecessors", [])
        return obj.invariant_path() in pred_str

    def doctor(self):
        """ Try to exam and fix the repository.
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            if obj.object_type() != "task" and obj.object_type() != "algorithm":
                continue

            for pred_object in obj.predecessors():
                if pred_object.is_zombie() or not pred_object.has_successor(obj):
                    print("The predecessor \n\t {} \n\t does not exists or do not \
has a link to object {}".format(pred_object, obj) )
                    choice = input("Would you like to remove the input or the algorithm? [Y/N]")
                    if choice == "Y":
                        obj.remove_arc_from(pred_object, single=True)
                        obj.remove_alias(obj.path_to_alias(pred_object.path))
                        obj.impress()

            for succ_object in obj.successors():
                if succ_object.is_zombie() or not succ_object.has_predecessor(obj):
                    print("The succecessor \n\t {} \n\t does not exists or do not \
has a link to object {}".format(succ_object, obj) )
                    choice = input("Would you like to remove the output? [Y/N]")
                    if choice == "Y":
                        obj.remove_arc_to(succ_object, single=True)

            for pred_object in obj.predecessors():
                if obj.path_to_alias(pred_object.invariant_path()) == "" and pred_object.object_type() != "algorithm":
                    print("The input {} of {} does not have alias, it will be removed".format(pred_object, obj))
                    choice = input("Would you like to remove the input or the algorithm? [Y/N]")
                    if choice == "Y":
                        obj.remove_arc_from(pred_object)
                        obj.impress()


            alias_to_path = obj.config_file.read_variable("alias_to_path", {})
            path_to_alias = obj.config_file.read_variable("path_to_alias", {})
            for path in path_to_alias.keys():
                project_path = csys.project_path(self.path)
                pred_obj = VObject(project_path+"/"+path)
                if not obj.has_predecessor(pred_obj):
                    print("There seems being a zombie alias to {} in {}".format(pred_obj, obj))
                    choice = input("Would you like to remove it? [Y/N]")
                    if choice == "Y":
                        obj.remove_alias(obj.path_to_alias(path))



    def copy_to(self, new_path):
        """ Copy the current objects and its containings to a new path.
        """
        queue = self.sub_objects_recursively()

        # Make sure the related objects are all impressed
        for obj in queue:
            if obj.object_type() != "task" and obj.object_type() != "algorithm":
                continue
            if not obj.is_impressed_fast():
                obj.impress()
        shutil.copytree(self.path, new_path)

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = os.path.normpath( os.path.join(new_path, self.relative_path(obj.path)) )
            new_object = VObject(norm_path)
            new_object.clean_flow()
            new_object.clean_impressions()

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = os.path.normpath( os.path.join(new_path +"/"+ self.relative_path(obj.path)) )
            new_object = VObject(norm_path)
            for pred_object in obj.predecessors():
                # if in the outside directory
                if self.relative_path(pred_object.path).startswith(".."):
                    pass
                else:
                    # if in the same tree
                    relative_path = self.relative_path(pred_object.path)
                    new_object.add_arc_from(VObject(new_path+"/"+relative_path))
                    alias1 = obj.path_to_alias(pred_object.invariant_path())
                    norm_path = os.path.normpath(new_path +"/"+ relative_path)
                    new_object.set_alias(alias1, VObject(norm_path).invariant_path())

            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    pass

        # Deal with the impression
        for obj in queue:
            # Calculate the absolute path of the new directory
            if obj.object_type() == "directory":
                norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))
                continue
            norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))
            new_object = VObject(norm_path)
            new_object.impress()

    def path_to_alias(self, path):
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        return path_to_alias.get(path, "")

    def alias_to_path(self, alias):
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        return alias_to_path.get(alias, "")

    def alias_to_impression(self, alias):
        path = self.alias_to_path(alias)
        obj = VObject(os.path.join(csys.project_path(self.path), path))
        return obj.impression()

    def has_alias(self, alias):
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        return alias in alias_to_path.keys()

    def remove_alias(self, alias):
        if alias == "":
            return
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        path = alias_to_path[alias]
        path_to_alias.pop(path)
        alias_to_path.pop(alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)
        self.config_file.write_variable("path_to_alias", path_to_alias)

    def set_alias(self, alias, path):
        if alias == "":
            return
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        path_to_alias[path] = alias
        alias_to_path[alias] = path
        self.config_file.write_variable("path_to_alias", path_to_alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)

    def clean_impressions(self):
        """ Clean the impressions of the object,
        this is used only when it is copied to a new place and needed to remove impression information.
        """
        self.config_file.write_variable("impressions", [])
        self.config_file.write_variable("impression", "")
        self.config_file.write_variable("output_md5s", {})
        self.config_file.write_variable("output_md5", "")

    def clean_flow(self):
        """ Clean all the alias, predecessors and successors,
        this is used only when it is copied to a new place and needed to remove impression information.
        """
        self.config_file.write_variable("alias_to_path", {})
        self.config_file.write_variable("path_to_alias", {})
        self.config_file.write_variable("predecessors", [])
        self.config_file.write_variable("successors", [])

    def move_to(self, new_path):
        """ move to another path
        """
        queue = self.sub_objects_recursively()

        # Make sure the related objects are all impressed
        all_impressed = True
        for obj in queue:
            if obj.object_type() != "task" and obj.object_type() != "algorithm":
                continue
            if not obj.is_impressed_fast():
                all_impressed = False
                print("The {} {} is not impressed, please impress it and try again".format(obj.object_type(), obj))
        if not all_impressed:
            return
        shutil.copytree(self.path, new_path)

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))
            new_object = VObject(norm_path)
            new_object.clean_flow()

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))
            new_object = VObject(norm_path)
            for pred_object in obj.predecessors():
                # if in the outside directory
                if self.relative_path(pred_object.path).startswith(".."):
                    new_object.add_arc_from(pred_object)
                    alias = obj.path_to_alias(pred_object.invariant_path())
                    new_object.set_alias(alias, pred_object.invariant_path())
                else:
                # if in the same tree
                    relative_path = self.relative_path(pred_object.path)
                    new_object.add_arc_from(VObject(new_path+"/"+relative_path) )
                    alias1 = obj.path_to_alias(pred_object.invariant_path())
                    alias2 = pred_object.path_to_alias(obj.invariant_path())
                    norm_path = os.path.normpath(new_path +"/"+ relative_path)
                    new_object.set_alias(alias1, VObject(norm_path).invariant_path())
                    VObject(norm_path).set_alias(alias2, new_object.invariant_path())

            for succ_object in obj.successors():
                # if in the outside directory
                if self.relative_path(succ_object.path).startswith(".."):
                    new_object.add_arc_to(succ_object)
                    succ_object.remove_arc_from(self)
                    alias = obj.path_to_alias(succ_object.invariant_path())
                    succ_object.remove_alias(alias)
                    succ_object.set_alias(alias, new_object.invariant_path())

        for obj in queue:
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    obj.remove_arc_from(pred_object)

            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    obj.remove_arc_to(succ_object)

        # Deal with the impression
        for obj in queue:
            # Calculate the absolute path of the new directory
            if obj.object_type() == "directory":
                continue
            norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))
            new_object = VObject(norm_path)

        if self.object_type() == "directory":
            norm_path = os.path.normpath(new_path +"/"+ self.relative_path(obj.path))

        shutil.rmtree(self.path)

    def rm(self):
        """
        Remove this object.
        The important this is to unalias
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    obj.remove_arc_from(pred_object)
                    alias = pred_object.path_to_alias(pred_object.path)
                    pred_object.remove_alias(alias)

            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    obj.remove_arc_to(succ_object)
                    alias = succ_object.path_to_alias(succ_object.path)
                    succ_object.remove_alias(alias)

        shutil.rmtree(self.path)

    def sub_objects(self):
        """ return a list of the sub_objects
        """
        sub_directories = os.listdir(self.path)
        sub_object_list = []
        for item in sub_directories:
            if os.path.isdir(self.path+"/"+item):
                obj = VObject(self.path+"/"+item)
                if obj.is_zombie():
                    continue
                sub_object_list.append(obj)
        return sub_object_list

    def sub_objects_recursively(self):
        """ Return a list of all the sub_objects
        """
        queue = [self]
        index = 0
        while index < len(queue):
            top_object = queue[index]
            queue += top_object.sub_objects()
            index += 1
        return queue

    def is_impressed_fast(self):
        """ Judge whether the file is impressed, with timestamp
        """
        logger.debug("VObject is_impressed_fast")
        consult_table = cherncache.impression_consult_table
        # FIXME cherncache should be replaced by some function called like cache
        last_consult_time, is_impressed = consult_table.get(self.path, (-1,-1))
        now = time.time()
        if now - last_consult_time < 1:
            # If the last consult time is less than 1 second ago, we can use the cache
            # But honestly, I don't remember why I set it to 1 second
            logger.debug("Time now: {} Last consult time: {}".format(now, last_consult_time))
            return is_impressed
        modification_time = csys.dir_mtime( csys.project_path(self.path) )
        if modification_time < last_consult_time:
            return is_impressed
        is_impressed = self.is_impressed()
        consult_table[self.path] = (time.time(), is_impressed)
        return is_impressed


    def pred_impressions(self):
        """ Get the impression dependencies
        """
        # FIXME An assumption is that all the predcessor's are impressed, if they are not, we should impress them first
        # Add check to this
        dependencies = []
        for pred in self.predecessors():
            dependencies.append(pred.impression())
        return sorted(dependencies,key=lambda x:x.uuid)

    def is_impressed(self, is_global=False):
        """ Judge whether the file is impressed
        """
        logger.debug("VObject is_impressed in %s", self.path)
        # Check whether there is an impression already
        impression = self.impression()
        logger.debug("Impression: %s", impression)
        if impression is None:
            return False

        logger.debug("Check the predecessors is impressed or not")
        # Fast check whether it is impressed
        for pred in self.predecessors():
            if not pred.is_impressed_fast():
                return False

        logger.debug("Check the dependencies is consistent with the predecessors")
        self_pred_impressions_uuid = [x.uuid for x in self.pred_impressions()]
        impr_pred_impressions_uuid = [x.uuid for x in impression.pred_impressions()]
        # Check whether the dependent impressions are the same as the impressed things
        if self_pred_impressions_uuid != impr_pred_impressions_uuid:
            return False

        logger.debug("Check the file change")
        # Check the file change: first to check the tree
        file_list = csys.tree_excluded(self.path)
        if file_list != impression.tree():
            return False

        for dirpath, dirnames, filenames in file_list:
            for f in filenames:
                if not filecmp.cmp(self.path+"/{}/{}".format(dirpath, f),
                               "{}/contents/{}/{}".format(impression.path, dirpath, f)):
                    return False
        return True

    def impress(self):
        """ Create an impression.
        The impressions are store in a directory .chern/impressions/[uuid]
        It is organized as following:
            [uuid]
            |------ contents
            |------ config.json
        In the config.json, the tree of the contents as well as the dependencies are stored.
        The object_type is also saved in the json file.
        The tree and the dependencies are sorted via name.
        """
        logger.debug("VObject impress: %s", self.path)
        object_type = self.object_type()
        if object_type != "task" and object_type != "algorithm":
            return
        logger.debug("Check whether it is impressed with is_impressed_fast")
        if self.is_impressed_fast():
            print("Already impressed.")
            return
        for pred in self.predecessors():
            if not pred.is_impressed_fast():
                pred.impress()
        impression = VImpression()
        impression.create(self)
        self.config_file.write_variable("impression", impression.uuid)

    def impression(self):
        """ Get the impression of the current object
        """
        uuid = self.config_file.read_variable("impression", "")
        if (uuid == ""):
            return None
        else:
            return VImpression(uuid)

    def is_submitted(self, machine="local"):
        """ Judge whether submitted or not. Return a True or False.
        [FIXME: incomplete]
        """
        if not self.is_impressed_fast():
            return False
        return False

        cherncc = ChernCommunicator.instance()
        if not self.is_impressed_fast():
            return False
        return cherncc.status(self.impression()) != "unsubmitted"

    def submit(self, machine = "local"):
        cherncc = ChernCommunicator.instance()
        self.deposit(machine)
        cherncc.execute([self.impression().uuid], machine)

    def deposit(self, machine = "local"):
        cherncc = ChernCommunicator.instance()
        if self.is_deposited():
            print("Already deposited")
            return
        if not self.is_impressed_fast():
            self.impress()
        for obj in self.predecessors():
            obj.deposit(machine)
        cherncc.deposit(self.impression(), machine)

    def is_deposited(self):
        if not self.is_impressed_fast():
            return False
        cherncc = ChernCommunicator.instance()
        return cherncc.is_deposited(self.impression()) == "TRUE"


    def readme(self):
        """
        FIXME
        Get the README String.
        I'd like it to support more
        """
        with open(self.path+"/.chern/README.md") as f:
            return f.read().strip("\n")

    def comment(self, line):
        with open(self.path+"/.chern/README.md", "a") as f:
            f.write(line + "\n")

    def cat(self, file_name):
        path = os.path.join(self.path, file_name)
        with open(path) as f:
            print(f.read().strip(""))

    def edit_readme(self):
        yaml_file = metadata.YamlFile(os.path.join(os.environ["HOME"], ".chern", "config.yaml"))
        print("???")
        editor = yaml_file.read_variable("editor", "vi")
        print(editor)
        file_name = os.path.join(self.path, ".chern/README.md")
        subprocess.call("{} {}".format(editor, file_name), shell=True)

