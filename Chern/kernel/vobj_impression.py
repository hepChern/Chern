""" Module for impression management
"""
import filecmp
import time
from logging import getLogger

from ..utils import csys
from .vobj_core import Core
from .vimpression import VImpression
from .chern_cache import ChernCache

CHERN_CACHE = ChernCache.instance()
logger = getLogger("ChernLogger")


class ImpressionManagement(Core):
    """ Class for impression management
    """
    def impress(self): # UnitTest: DONE
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
        logger.debug("VObject impress: %s", self.path)
        object_type = self.object_type()
        if object_type not in ("task", "algorithm"):
            sub_objects = self.sub_objects()
            for sub_object in sub_objects:
                sub_object.impress()
            return
        logger.debug("Check whether it is impressed with is_impressed_fast")
        if self.is_impressed_fast():
            logger.warning("Already impressed: %s", self.path)
            return
        for pred in self.predecessors():
            if not pred.is_impressed_fast():
                pred.impress()
        impression = VImpression()
        impression.create(self)
        self.config_file.write_variable("impression", impression.uuid)
        # update the impression_consult_table, since the impression is changed
        consult_table = CHERN_CACHE.impression_consult_table
        consult_table[self.path] = (-1, -1)

    def is_impressed(self): # pylint: disable=too-many-return-statements # UnitTest: DONE
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
        impression_tree = impression.tree()

        # Check the file list is the same as the impression tree
        # if file_list != impression.tree():
        #     return False
        if csys.sorted_tree(file_list) != csys.sorted_tree(impression_tree):
            return False

        # FIXME Add the Unit Test for this part
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        for alias in alias_to_path.keys():
            if not impression.has_alias(alias):
                return False
            if not self.alias_to_impression(alias):
                return False
            uuid1 = self.alias_to_impression(alias).uuid
            uuid2 = impression.alias_to_impression_uuid(alias)
            if uuid1 != uuid2:
                return False


        for dirpath, dirnames, filenames in file_list: # pylint: disable=unused-variable
            for f in filenames:
                if not filecmp.cmp(f"{self.path}/{dirpath}/{f}",
                                   f"{impression.path}/contents/{dirpath}/{f}"):
                    return False
        return True

    def clean_impressions(self): # UnitTest: DONE
        """ Clean the impressions of the object,
        this is used only when it is copied to a new place and
        needed to remove impression information.
        """
        if not self.is_task_or_algorithm():
            sub_objects = self.sub_objects()
            for sub_object in sub_objects:
                sub_object.clean_impressions()
            return
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

    def is_impressed_fast(self): # UnitTest: DONE
        """ Judge whether the file is impressed, with timestamp
        """
        logger.debug("VObject is_impressed_fast")
        consult_table = CHERN_CACHE.impression_consult_table
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
            logger.debug("Time now: %lf", now)
            logger.debug("Last consult time: %lf", last_consult_time)
            return is_impressed
        modification_time_from_cache, modification_consult_time = \
                CHERN_CACHE.project_modification_time
        if modification_time_from_cache is None or now - modification_consult_time > 1:
            modification_time = csys.dir_mtime(self.project_path())
            CHERN_CACHE.project_modification_time = modification_time, now
        else:
            modification_time = modification_time_from_cache
        if modification_time < last_consult_time:
            return is_impressed
        is_impressed = self.is_impressed()
        consult_table[self.path] = (time.time(), is_impressed)
        return is_impressed

    def pred_impressions(self): # UnitTest: DONE
        """ Get the impression dependencies
        """
        # FIXME An assumption is that all the predcessor's are impressed,
        # if they are not, we should impress them first
        # Add check to this
        dependencies = []
        for pred in self.predecessors():
            dependencies.append(pred.impression())
        return sorted(dependencies, key=lambda x: x.uuid)

    def impression(self): # UnitTest: DONE
        """ Get the impression of the current object
        """
        uuid = self.config_file.read_variable("impression", "")
        if uuid == "":
            return None
        return VImpression(uuid)

    def status(self, consult_id=None): # UnitTest: DONE
        """ Consult the status of the object
            There should be only two status locally: new|impressed
        """
        # If it is already asked, just give us the answer
        logger.debug("VTask status: Consulting status of %s", self.path)
        if consult_id:
            consult_table = CHERN_CACHE.status_consult_table
            cid, status = consult_table.get(self.path, (-1,-1))
            if cid == consult_id:
                return status

        if not self.is_task_or_algorithm():
            for sub_object in self.sub_objects():
                status = sub_object.status(consult_id)
                if status == "new":
                    return "new"
            return "impressed"

        if not self.is_impressed_fast():
            if consult_id:
                consult_table[self.path] = (consult_id, "new")
            return "new"

        status = "impressed"
        if consult_id:
            consult_table[self.path] = (consult_id, status)
        return status
