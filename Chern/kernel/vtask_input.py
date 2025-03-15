from ..utils import metadata
from ..utils import csys
from . import VObject as vobj
from . import VTask as vtsk
from . import VAlgorithm as valg
from logging import getLogger
from os.path import join
logger = getLogger("ChernLogger")


class InputManager:
    # Abandoned method, replaced by send
    def add_source(self, path):
        """
        After add source, the status of the task should be done
        """
        md5 = csys.dir_md5(path)
        data_file = metadata.ConfigFile(join(self.path, "data.json"))
        data_file.write_variable("md5", md5)
        self.impress()

    def send(self, path):
        md5 = csys.dir_md5(path)
        self.set_input_md5(md5)
        self.impress()
        self.send_data(path)

    def add_algorithm(self, path):
        """
        Add a algorithm
        """
        obj = vobj.VObject(path)
        if obj.object_type() != "algorithm":
            print("You are adding {} type object as".format(
                obj.object_type()
            ) + " algorithm. The algorithm is required to be an algorithm.")
            return
        # Check whether the algorithm is already in the dependency diagram
        if obj.has_predecessor_recursively(self):
            print("The object is already in the dependency diagram of "
                  "the ``algorithm'', which will cause a loop.")
            return

        algorithm = self.algorithm()
        if algorithm is not None:
            print("Already have algorithm, will replace it")
            self.remove_algorithm()
        self.add_arc_from(vobj.VObject(path))

    def remove_algorithm(self):
        """
        Remove the algorithm
        """
        algorithm = self.algorithm()
        if algorithm is None:
            print("Nothing to remove")
        else:
            self.remove_arc_from(algorithm)

    def algorithm(self):
        """
        Return the algorithm
        """
        predecessors = self.predecessors()
        for pred_object in predecessors:
            if pred_object.object_type() == "algorithm":
                return valg.VAlgorithm(pred_object.path)
        return None

    def add_input(self, path, alias):
        """ FIXME: judge the input type
        """
        obj = vobj.VObject(path)
        if obj.object_type() != "task":
            print("You are adding {} type object as".format(
                obj.object_type()
                ) + " input. The input is required to be a task.")
            return

        if obj.has_predecessor_recursively(self):
            print("The object is already in the dependency diagram of "
                  "the ``input'', which will cause a loop.")
            return

        if self.has_alias(alias):
            print("The alias already exists. "
                  "The original input and alias will be replaced.")
            project_path = csys.project_path(self.path)
            original_object = vobj.VObject(
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
        obj = vobj.VObject(join(project_path, path))
        self.remove_arc_from(obj)
        self.remove_alias(alias)

    def inputs(self):
        """ Input data """
        inputs = filter(
            lambda x: (x.object_type() == "task"), self.predecessors()
            )
        return list(map(lambda x: vtsk.VTask(x.path), inputs))

    def outputs(self):
        """ Output data. """
        outputs = filter(
            lambda x: x.object_type() == "task", self.successors()
            )
        return list(map(lambda x: vtsk.VTask(x.path), outputs))
