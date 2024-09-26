from Chern.kernel.VObject import VObject
from Chern.kernel import VAlgorithm
from Chern.utils import metadata
from Chern.utils import csys

from logging import getLogger
from os.path import join
logger = getLogger("ChernLogger")


class InputManager:
    def add_source(self, path):
        """
        After add source, the status of the task should be done
        """
        md5 = csys.dir_md5(path)
        data_file = metadata.ConfigFile(join(self.path, "data.json"))
        data_file.write_variable("md5", md5)
        self.impress()

    def add_algorithm(self, path):
        """
        Add a algorithm
        """
        algorithm = self.algorithm()
        if algorithm is not None:
            print("Already have algorithm, will replace it")
            self.remove_algorithm()
        self.add_arc_from(VObject(path))

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
                return VAlgorithm.VAlgorithm(pred_object.path)
        return None

    def add_input(self, path, alias):
        """ FIXME: judge the input type
        """
        obj = VObject(path)
        if obj.object_type() != "task":
            print("You are adding {} type object as input. The input is required to be a task.".format(obj.object_type()))
            return

        if self.has_alias(alias):
            print("The alias already exists. The original input and alias will be replaced.")
            project_path = csys.project_path(self.path)
            original_object = VObject(
                join(project_path, self.alias_to_path(alias))
            )
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
        obj = VObject(join(project_path, path))
        self.remove_arc_from(obj)
        self.remove_alias(alias)
