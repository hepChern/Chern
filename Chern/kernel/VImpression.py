""" Helper class for impress operation
"""
from Chern.utils import csys
from Chern.utils import metadata
from Chern.utils.pretty import colorize
from Chern.utils.utils import color_print

class VImpression(object):
    def __init__(self, uuid = None):
        if uuid is None:
            self.uuid = csys.generate_uuid()
        else:
            self.uuid = uuid
        self.path = csys.project_path() + "/.chern/impressions/" + self.uuid
        self.config_file = metadata.ConfigFile(self.path+"/config.json")
        self.tarfile = self.path + "/packed" + self.uuid + ".tar.gz"

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

    def clear(self):
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
        return self.config_file.read_variable("dependencies", [])

    def create(self, obj):
        """ Create this impression with a VObject file
        """
        # Create an impression directory and
        file_list = csys.tree_excluded(obj.path)
        csys.mkdir(self.path+"/contents".format(self.uuid))
        for dirpath, dirnames, filenames in file_list:
            for f in filenames:
                csys.copy(obj.path+"/{}/{}".format(dirpath, f),
                          self.path+"/contents/{}/{}".format(dirpath, f))

        # Write tree and dependencies to the configuration file
        dependencies = obj.pred_impressions()
        self.config_file.write_variable("tree", file_list)
        self.config_file.write_variable("dependencies", dependencies)


        # Write the basic metadata to the configuration file
        # self.config_file.write_variable("object_type", obj.object_type)
        parent_impression = obj.impression()
        if (parent_impression is None):
            parents = []
        else:
            parents = parent_impression.parents()
            parents.append(parent_impression.uuid)
            parent_impression.clear()
        self.config_file.write_variable("parents", parents)
        self.pack()
