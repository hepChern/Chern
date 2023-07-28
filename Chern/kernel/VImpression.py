""" Helper class for impress operation
"""
from Chern.utils import csys
from Chern.utils import metadata
from Chern.utils.pretty import colorize
from Chern.utils.utils import color_print
from logging import getLogger
logger = getLogger("ChernLogger")

class VImpression(object):
    def __init__(self, uuid = None):
        if uuid is None:
            self.uuid = csys.generate_uuid()
        else:
            self.uuid = uuid
        self.path = csys.project_path() + "/.chern/impressions/" + self.uuid
        self.config_file = metadata.ConfigFile(self.path+"/config.json")
        self.tarfile = self.path + "/packed" + self.uuid + ".tar.gz"

    def __str__(self) -> str:
        return self.uuid

    def is_packed(self):
        # We should check whether it is affacted by other things
        return csys.exists(self.path + "/packed" + self.uuid + ".tar.gz")

    def pack(self):
        """ Pack the impression
        """
        if (self.is_packed()):
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
        pass

    def difference(self):
        """ Calculate the difference between this and another impression
        """

    def tree(self):
        return self.config_file.read_variable("tree")

    def parents(self):
        return self.config_file.read_variable("parents", [])

    def parent(self):
        parents = self.parents()
        if (parents):
            return parents[-1]
        else:
            return None

    def pred_impressions(self):
        """ Get the impression dependencies
        """
        # FIXME An assumption is that all the predcessor's are impressed, if they are not, we should impress them first
        # Add check to this
        dependencies_uuid = self.config_file.read_variable("dependencies", [])
        dependencies = [VImpression(uuid) for uuid in dependencies_uuid]
        return dependencies 

    def create(self, obj):
        """ Create this impression with a VObject file
        """
        logger.debug("Creating impression {}".format(self.uuid))
        # Create an impression directory and copy the files to it
        file_list = csys.tree_excluded(obj.path)
        csys.mkdir(self.path+"/contents".format(self.uuid))
        for dirpath, dirnames, filenames in file_list:
            for f in filenames:
                csys.copy(obj.path+"/{}/{}".format(dirpath, f),
                          self.path+"/contents/{}/{}".format(dirpath, f))

        # Write tree and dependencies to the configuration file
        dependencies = obj.pred_impressions()
        dependencies_uuid = [dep.uuid for dep in dependencies]
        self.config_file.write_variable("object_type", obj.object_type())
        self.config_file.write_variable("tree", file_list)
        self.config_file.write_variable("dependencies", dependencies_uuid)


        # Write the basic metadata to the configuration file
        # self.config_file.write_variable("object_type", obj.object_type)
        parent_impression = obj.impression()
        if (parent_impression is None):
            parents = []
        else:
            parents = parent_impression.parents()
            parents.append(parent_impression.uuid)
            parent_impression.clean()
        self.config_file.write_variable("parents", parents)
        self.pack()
