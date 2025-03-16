""" This module is used to manage the alias of the vobj.
"""
import os
from logging import getLogger

from Chern.utils import csys
from . import VObject as vobj
from .vobj_core import Core

logger = getLogger("ChernLogger")


class AliasManagement(Core):
    """ This class is used to manage the alias of the vobj.
    """
    def path_to_alias(self, path):
        """ Get the alias of the vobj by the path."""
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        return path_to_alias.get(path, "")

    def alias_to_path(self, alias):
        """ Get the path of the vobj by the alias."""
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        return alias_to_path.get(alias, "")

    def alias_to_impression(self, alias):
        """ Get the impression of the vobj by the alias."""
        path = self.alias_to_path(alias)
        obj = vobj.VObject(os.path.join(csys.project_path(self.path), path))
        return obj.impression()

    def has_alias(self, alias):
        """ Check if the alias is in the alias list."""
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        return alias in alias_to_path.keys()

    def remove_alias(self, alias):
        """ Remove the alias from the alias list."""
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
        """ Set the alias of the vobj by the path."""
        if alias == "":
            return
        path_to_alias = self.config_file.read_variable("path_to_alias", {})
        alias_to_path = self.config_file.read_variable("alias_to_path", {})
        path_to_alias[path] = alias
        alias_to_path[alias] = path
        self.config_file.write_variable("path_to_alias", path_to_alias)
        self.config_file.write_variable("alias_to_path", alias_to_path)
