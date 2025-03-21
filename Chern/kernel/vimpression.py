""" Helper class for impress operation
"""
from os.path import join
from logging import getLogger

from ..utils import csys
from ..utils import metadata

logger = getLogger("ChernLogger")

class VImpression():
    """ A class to represent an impression
    """
    uuid = None
    def __init__(self, uuid = None):
        """ Initialize the impression
        """
        if uuid is None:
            self.uuid = csys.generate_uuid()
        else:
            self.uuid = uuid
        self.path = csys.project_path() + "/.chern/impressions/" + self.uuid
        self.config_file = metadata.ConfigFile(self.path+"/config.json")
        self.tarfile = self.path + "/packed" + self.uuid + ".tar.gz"

    def __str__(self):
        """ Print the impression
        """
        return self.uuid

    def is_zombie(self):
        """ Check whether the impression is a zombie
        """
        return not csys.exists(self.path)

    def is_packed(self):
        """ Check whether the impression is packed
        """
        return csys.exists(
                join(self.path, "/packed", self.uuid, ".tar.gz")
                )

    def pack(self):
        """ Pack the impression
        """
        if self.is_packed():
            return
        output_name = self.path + "/packed" + self.uuid
        csys.make_archive(output_name, self.path+"/contents")

    def clean(self):
        """ Clean the impression
        """
        csys.rm_tree(self.path+"/contents")

    def upack(self):
        """ Unpack the impression
        """
        # FIXME: to be implemented

    def difference(self):
        """ Calculate the difference between this and another impression
        """
        # FIXME: to be implemented

    def tree(self):
        """ Get the tree of the impression
        """
        return self.config_file.read_variable("tree")

    def parents(self):
        """ Get the parents of the impression
        """
        return self.config_file.read_variable("parents", [])

    def parent(self):
        """ Get the parent of the impression
        """
        parents = self.parents()
        if parents:
            return parents[-1]
        return None

    def pred_impressions(self):
        """ Get the impression dependencies
        """
        # FIXME An assumption is that all the predcessor's are impressed,
        # if they are not, we should impress them first
        # Need to add check to this
        dependencies_uuid = self.config_file.read_variable("dependencies", [])
        dependencies = [VImpression(uuid) for uuid in dependencies_uuid]
        return dependencies

    def create(self, obj):
        """ Create this impression with a VObject file
        """
        print(f"Creating impression {self.uuid}")
        # Create an impression directory and copy the files to it
        file_list = csys.tree_excluded(obj.path)
        csys.mkdir(self.path+"/contents")
        for dirpath, dirnames, filenames in file_list: # pylint: disable=unused-variable
            for f in filenames:
                csys.copy(f"{obj.path}/{dirpath}/{f}",
                          f"{self.path}/contents/{dirpath}/{f}")

        # Write tree and dependencies to the configuration file
        dependencies = obj.pred_impressions()
        dependencies_uuid = [dep.uuid for dep in dependencies]
        self.config_file.write_variable("object_type", obj.object_type())
        self.config_file.write_variable("tree", file_list)
        self.config_file.write_variable("dependencies", dependencies_uuid)

        self.config_file.write_variable("current_path", obj.invariant_path())

        if obj.is_task_or_algorithm():
            alias_to_imp = {}
            alias_to_path = obj.config_file.read_variable("alias_to_path", {})
            for alias, path in alias_to_path.items(): # pylint: disable=unused-variable
                alias_to_imp[alias] = obj.alias_to_impression(alias).uuid
            self.config_file.write_variable("alias_to_impression", alias_to_imp)

        # Write the basic metadata to the configuration file
        # self.config_file.write_variable("object_type", obj.object_type)
        parent_impression = obj.impression()
        if parent_impression is None:
            parents = []
        else:
            parents = parent_impression.parents()
            parents.append(parent_impression.uuid)
            if parent_impression.is_zombie():
                parent_impression.clean()
        self.config_file.write_variable("parents", parents)
        self.pack()
