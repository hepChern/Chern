import filecmp
from .chern_cache import ChernCache
from .VImpression import VImpression
import time
from ..utils import csys

from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class ImpressionManagement:
    def impress(self):
        """ Create an impression.
        The impressions are store in a directory .chern/impressions/[uuid]
        It is organized as following:
            [uuid]
            |------ contents
            |------ config.json
        In the config.json, the tree of the contents as well as
        the dependencies are stored.
        The object_type is also saved in the json file.
        The tree and the dependencies are sorted via name.
        """
        print("Impressing: {}".format(self.path))
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
        # update the impression_consult_table, since the impression is changed
        consult_table = cherncache.impression_consult_table
        consult_table[self.path] = (-1, -1)

    def is_impressed(self, is_global=False):
        """ Judge whether the file is impressed
        """
        logger.debug("VObject is_impressed in %s", self.path)
        # Check whether there is an impression already
        impression = self.impression()
        logger.debug("Impression: %s", impression)
        if impression is None or impression.is_zombie():
            return False

        logger.debug("Check the predecessors is impressed or not")
        # Fast check whether it is impressed
        for pred in self.predecessors():
            if not pred.is_impressed_fast():
                return False

        logger.debug("Check the dependencies is consistent "
                     "with the predecessors")
        self_pred_impressions_uuid = [x.uuid for x in self.pred_impressions()]
        impr_pred_impressions_uuid = [
            x.uuid for x in impression.pred_impressions()
        ]
        # Check whether the dependent impressions
        # are the same as the impressed things
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
                                   "{}/contents/{}/{}".format(
                                       impression.path, dirpath, f
                                    )):
                    return False
        return True

    def clean_impressions(self):
        """ Clean the impressions of the object,
        this is used only when it is copied to a new place and
        needed to remove impression information.
        """
        self.config_file.write_variable("impressions", [])
        self.config_file.write_variable("impression", "")
        self.config_file.write_variable("output_md5s", {})
        self.config_file.write_variable("output_md5", "")

    def clean_flow(self):
        """ Clean all the alias, predecessors and successors,
        this is used only when it is copied to a new place
        and needed to remove impression information.
        """
        self.config_file.write_variable("alias_to_path", {})
        self.config_file.write_variable("path_to_alias", {})
        self.config_file.write_variable("predecessors", [])
        self.config_file.write_variable("successors", [])

    def is_impressed_fast(self):
        """ Judge whether the file is impressed, with timestamp
        """
        logger.debug("VObject is_impressed_fast")
        consult_table = cherncache.impression_consult_table
        # FIXME cherncache should be replaced
        # by some function called like cache
        (last_consult_time, is_impressed) = consult_table.get(
            self.path, (-1, -1)
        )
        now = time.time()
        if now - last_consult_time < 1:
            # If the last consult time is less than 1 second ago,
            # we can use the cache
            # But honestly, I don't remember why I set it to 1 second
            logger.debug("Time now: {}".format(now))
            logger.debug("Last consult time: {}".format(last_consult_time))
            return is_impressed
        modification_time = csys.dir_mtime(csys.project_path(self.path))
        if modification_time < last_consult_time:
            return is_impressed
        is_impressed = self.is_impressed()
        consult_table[self.path] = (time.time(), is_impressed)
        return is_impressed

    def pred_impressions(self):
        """ Get the impression dependencies
        """
        # FIXME An assumption is that all the predcessor's are impressed,
        # if they are not, we should impress them first
        # Add check to this
        dependencies = []
        for pred in self.predecessors():
            dependencies.append(pred.impression())
        return sorted(dependencies, key=lambda x: x.uuid)

    def impression(self):
        """ Get the impression of the current object
        """
        uuid = self.config_file.read_variable("impression", "")
        if (uuid == ""):
            return None
        else:
            return VImpression(uuid)
