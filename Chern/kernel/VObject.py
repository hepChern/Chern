""" Virtual base class for all ```directory'', ``task'', ``algorithm''
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    VObject:
    # Methods:
        + __init__:
            It should be initialized with a absolute path.
            The initialization gets variable "path" and "config_file".
            It is quite light-weight to create a VObject.
            A VObject can be abandoned after using
            and create another when needed.

        + __str__, __repr__:
            For print

        + invariant_path:
            Return the path relative to the project root
        + relative_path(a_path);
            Return the path of the VObject relative to a_path

        + object_type:
            Return the type of the object: project,
            task, directory, or empty("")
        + is_zombine
            To judge whether this object has a type

        + color_tag: (Maybe put it somewhere else?)
            For print

        + ls:
            Realization of "ls" call o.ls()
            will give you the contents of the object

        + add_arc_from(obj)
        + remove_arc_from(obj, single=False)
        + add_arc_to(obj)
        + remove_arc_from(obj, single=False):
            Add or remove arcs,
            the "single" variable is only used for debug usage.

        + successors
        + predecessors:
            Get [objects]
        + has_successor(obj)
        + has_predessor(obj)
            Judge whether obj is the succ/pred of this obj

        + doctor:
            Judge whether it is a good object(with all arc linked)

        + copy_to:
            Copy the object and its contains to a new path. Before the copy,
            all objects in the directory will be impressed.
            The arcs within the directory will be kept
            and outsides will be removed.
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
from os.path import join
import subprocess
from ..utils import csys
from ..utils import metadata

from .vobj_arc_management import ArcManagement
from .vobj_core import Core
from .vobj_alias_management import AliasManagement
from .vobj_impression import ImpressionManagement
from .vobj_execution import ExecutionManagement

from .ChernCache import ChernCache

from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class VObject(Core, ArcManagement, AliasManagement,
              ImpressionManagement, ExecutionManagement):
    """ Virtual class of the objects,
    including VData, VAlgorithm and VDirectory
    """

    # Initialization and Representation
    def __init__(self, path):
        """ Initialize a instance of the object.
        All the information is directly read from and write to the disk.
        parameter ``path'' is allowed to be a string
        begin with empty characters.
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

    # Path handling, type and status
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

    def is_task(self):
        """ Judge whether it is a task.
        """
        return self.object_type() == "task"

    def is_algorithm(self):
        """ Judge whether it is an algorithm.
        """
        return self.object_type() == "algorithm"

    def is_task_or_algorithm(self):
        """ Judge whether it is a task or an algorithm.
        """
        if self.object_type() == "task":
            return True
        if self.object_type() == "algorithm":
            return True
        return False

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

    def cat(self, file_name):
        path = os.path.join(self.path, file_name)
        with open(path) as f:
            print(f.read().strip(""))

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

    def edit_readme(self):
        yaml_file = metadata.YamlFile(
            join(os.environ["HOME"], ".chern", "config.yaml")
        )
        editor = yaml_file.read_variable("editor", "vi")
        file_name = os.path.join(self.path, ".chern/README.md")
        subprocess.call("{} {}".format(editor, file_name), shell=True)
