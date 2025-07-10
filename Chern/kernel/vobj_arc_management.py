""" The module for arc management of VObject
"""
from os.path import join
from time import time
from logging import getLogger

from ..utils import csys
from .vobj_core import Core

from .chern_cache import ChernCache

CHERN_CACHE = ChernCache.instance()
logger = getLogger("ChernLogger")


class ArcManagement(Core):
    """ The class for arc management of VObject
    """

    def add_arc_from(self, obj):
        """
        Add a link from the object contained in `path` to this object.

        Example:
            o  --*--> (o) ----> o
           (o) --*-->  o

        Args:
            obj: The object to link from.
        """
        succ_str = obj.config_file.read_variable("successors", [])
        succ_str.append(self.invariant_path())
        obj.config_file.write_variable("successors", succ_str)

        pred_str = self.config_file.read_variable("predecessors", [])
        pred_str.append(obj.invariant_path())
        self.config_file.write_variable("predecessors", pred_str)

    def remove_arc_from(self, obj, single=False):
        """
        Remove a link from the object contained in `path`.

        If `single` is set to True, only remove the arc in this object.
        If `single` is set to False, remove the arc globally.

        Example:
            o  --X--> (o) ----> o  (Remove this arc)
           (o) --X-->  o

        Args:
            obj: The object to unlink from.
            single (bool): Whether to remove the arc only in this object.
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
        """
        Add a link from this object to the object contained in `path`.

        Example:
            o  -----> (o) --*-->  o
                       o  --*--> (o)

        Args:
            obj: The object to link to.
        """
        pred_str = obj.config_file.read_variable("predecessors", [])
        pred_str.append(self.invariant_path())
        obj.config_file.write_variable("predecessors", pred_str)

        succ_str = self.config_file.read_variable("successors", [])
        succ_str.append(obj.invariant_path())
        self.config_file.write_variable("successors", succ_str)

    def remove_arc_to(self, obj, single=False):
        """
        Remove a link to the object contained in `path`.

        If `single` is set to True, only remove the arc in this object.
        If `single` is set to False, remove the arc globally.

        Example:
            o  -----> (o) --X-->  o  (Remove this arc)
                       o  --X--> (o)

        Args:
            obj: The object to unlink from.
            single (bool): Whether to remove the arc only in this object.
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
            successors.append(self.get_vobject(f"{project_path}/{path}"))
        return successors

    def predecessors(self):
        """ The predecessosr of the current object
        Return a list of [object]
        """
        pred_str = self.config_file.read_variable("predecessors", [])
        predecessors = []
        project_path = csys.project_path(self.path)
        for path in pred_str:
            predecessors.append(self.get_vobject(f"{project_path}/{path}"))
        return predecessors

    def has_successor(self, obj): # UnitTest: DONE
        """ Judge whether the object has the specific successor
        """
        succ_str = self.config_file.read_variable("successors", [])
        return obj.invariant_path() in succ_str

    def has_predecessor(self, obj): # UnitTest: DONE
        """ Judge whether the object has the specific predecessor
        """
        pred_str = self.config_file.read_variable("predecessors", [])
        return obj.invariant_path() in pred_str

    def has_predecessor_recursively(self, obj): # UnitTest: DONE
        """ Judge whether the object has the specific predecessor recursively
        """
        # The object itself is the predecessor of itself
        if self.invariant_path() == obj.invariant_path():
            return True

        pred_str = self.config_file.read_variable("predecessors", [])
        if obj.invariant_path() in pred_str:
            return True
        # Use cache to avoid infinite loop
        consult_table = CHERN_CACHE.predecessor_consult_table
        (last_consult_time, has_predecessor) = consult_table.get(
            self.path, (-1, False)
        )
        now = time()
        if now - last_consult_time < 1:
            return has_predecessor

        modification_time = csys.dir_mtime(csys.project_path(self.path))
        if modification_time < last_consult_time:
            return has_predecessor

        for pred_path in pred_str:
            project_path = csys.project_path(self.path)
            pred_obj = self.get_vobject(f"{project_path}/{pred_path}")
            if pred_obj.has_predecessor_recursively(obj):
                consult_table[self.path] = (time(), True)
                return True
        consult_table[self.path] = (time(), False)
        return False

    def doctor(self):
        """ Try to exam and fix the repository.
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            if not obj.is_task_or_algorithm():
                continue

            self.doctor_predecessor(obj)
            self.doctor_successor(obj)
            self.doctor_alias(obj)
            self.doctor_path_to_alias(obj)

    def doctor_predecessor(self, obj):
        """ Doctor the predecessors of the object
        """
        for pred_object in obj.predecessors():
            if pred_object.is_zombie() or \
                    not pred_object.has_successor(obj):
                print(f"The predecessor \n\t {pred_object} \n\t "
                      f"does not exist or does not have a link "
                      f"to object {obj}")
                choice = input(
                    "Would you like to remove the input or the algorithm? "
                    "[Y/N]: "
                )
                if choice.upper() == "Y":
                    obj.remove_arc_from(pred_object, single=True)
                    obj.remove_alias(obj.path_to_alias(pred_object.path))
                    obj.impress()


    def doctor_successor(self, obj):
        """ Doctor the successors of the object
        """
        for succ_object in obj.successors():
            if succ_object.is_zombie() or \
                    not succ_object.has_predecessor(obj):
                print("The successor")
                print(f"\t {succ_object}")
                print(f"\t does not exist or does not have a link to object {obj}")
                choice = input("Would you like to remove the output? [Y/N]")
                if choice == "Y":
                    obj.remove_arc_to(succ_object, single=True)

    def doctor_alias(self, obj):
        """ Doctor the alias of the object
        """
        for pred_object in obj.predecessors():
            if obj.path_to_alias(pred_object.invariant_path()) == "" and \
                    not pred_object.is_algorithm():
                print(f"The input {pred_object} of {obj} does not have an alias, "
                      f"it will be removed.")
                choice = input(
                    "Would you like to remove the input or the algorithm? [Y/N]: "
                    )
                if choice.upper() == "Y":
                    obj.remove_arc_from(pred_object)
                    obj.impress()

    def doctor_path_to_alias(self, obj):
        """ Doctor the alias of the object recursively
        """
        path_to_alias = obj.config_file.read_variable("path_to_alias", {})
        for path in path_to_alias.keys():
            project_path = csys.project_path(self.path)
            pred_obj = self.get_vobject(f"{project_path}/{path}")
            if not obj.has_predecessor(pred_obj):
                print("There seems to be a zombie alias to")
                print(f"{pred_obj} in {obj}")
                choice = input("Would you like to remove it? [Y/N]: ")
                if choice.upper() == "Y":
                    obj.remove_alias(obj.path_to_alias(path))

    def add_input(self, path, alias):
        """ add input
        """
        if not self.is_task_or_algorithm():
            print(f"You are adding input to {self.object_type()} type object. "
                  "The input is required to be a task or an algorithm.")
            return

        obj = self.get_vobject(path)
        if obj.object_type() != self.object_type():
            print(f"You are adding {obj.object_type()} type object as"
                   " input. The input is required to be a {self.object_type()}.")
            return

        if obj.has_predecessor_recursively(self):
            print("The object is already in the dependency diagram of "
                  "the ``input'', which will cause a loop.")
            return

        # if the obj is already an input, reject to add it
        if self.has_predecessor(obj):
            print("The input already exists.")
            return

        if self.has_alias(alias):
            print("The alias already exists. "
                  "The original input and alias will be replaced.")
            project_path = csys.project_path(self.path)
            original_object = self.get_vobject(
                join(project_path, self.alias_to_path(alias))
            )
            self.remove_arc_from(original_object)
            self.remove_alias(alias)

        self.add_arc_from(obj)
        self.set_alias(alias, obj.invariant_path())

    def remove_input(self, alias):
        """ Remove the input """
        path = self.alias_to_path(alias)
        if path == "":
            print("Alias not found")
            return
        project_path = csys.project_path(self.path)
        obj = self.get_vobject(join(project_path, path))
        self.remove_arc_from(obj)
        self.remove_alias(alias)
