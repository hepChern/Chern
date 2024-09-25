from Chern.utils import csys
from Chern.kernel.ChernCache import ChernCache
import Chern.kernel.VObject as vobj

from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class ArcManagement:
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
            successors.append(vobj.VObject(project_path+"/"+path))
        return successors

    def predecessors(self):
        """ The predecessosr of the current object
        Return a list of [object]
        """
        pred_str = self.config_file.read_variable("predecessors", [])
        predecessors = []
        project_path = csys.project_path(self.path)
        for path in pred_str:
            predecessors.append(vobj.VObject(project_path+"/"+path))
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
            if obj.object_type() != "task" \
                    and obj.object_type() != "algorithm":
                continue

            for pred_object in obj.predecessors():
                if pred_object.is_zombie() or not pred_object.has_successor(obj):
                    print(f"The predecessor \n\t {pred_object} \n\t does not exist or does not "
                          f"have a link to object {obj}")
                    choice = input("Would you like to remove the input or the algorithm? [Y/N]: ")
                    if choice.upper() == "Y":
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
                if (obj.path_to_alias(pred_object.invariant_path()) == "" and 
                    pred_object.object_type() != "algorithm"):
                    print(f"The input {pred_object} of {obj} does not have an alias, it will be removed.")
                    choice = input("Would you like to remove the input or the algorithm? [Y/N]: ")
                    if choice.upper() == "Y":
                        obj.remove_arc_from(pred_object)
                        obj.impress()

            path_to_alias = obj.config_file.read_variable("path_to_alias", {})
            for path in path_to_alias.keys():
                project_path = csys.project_path(self.path)
                pred_obj = vobj.VObject(f"{project_path}/{path}")
                if not obj.has_predecessor(pred_obj):
                    print(f"There seems to be a zombie alias to {pred_obj} in {obj}")
                    choice = input("Would you like to remove it? [Y/N]: ")
                    if choice.upper() == "Y":
                        obj.remove_alias(obj.path_to_alias(path))

