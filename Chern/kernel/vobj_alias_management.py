import os
from Chern.utils import csys
from Chern.kernel.ChernCache import ChernCache
import Chern.kernel.VObject as vobj

from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class AliasManagement:
    def path_to_alias(self, path):
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        return path_to_alias.get(path, "")

    def alias_to_path(self, alias):
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        return alias_to_path.get(alias, "")

    def alias_to_impression(self, alias):
        path = self.alias_to_path(alias)
        obj = vobj.VObject(os.path.join(csys.project_path(self.path), path))
        return obj.impression()

    def has_alias(self, alias):
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        return alias in alias_to_path.keys()

    def remove_alias(self, alias):
        if alias == "":
            return
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        path = alias_to_path[alias]
        path_to_alias.pop(path)
        alias_to_path.pop(alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)
        self.config_file.write_variable("path_to_alias", path_to_alias)

    def set_alias(self, alias, path):
        if alias == "":
            return
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        path_to_alias[path] = alias
        alias_to_path[alias] = path
        self.config_file.write_variable("path_to_alias", path_to_alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)