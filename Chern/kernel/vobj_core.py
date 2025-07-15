# pylint: disable=too-many-public-methods
""" The Core of the VObject
This module defines the abstract base class `Core` for VObjects,
Total implemented methods: 10
Unit tests: 8
"""
import os
from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Optional, List

from ..utils import csys
from ..utils import metadata

if TYPE_CHECKING:
    from .vobject import VObject
    from .vimpression import VImpression

logger = getLogger("ChernLogger")

class Core(ABC):
    """ The core of the VObject
    """
    def __init__(self, path: str) -> None: # Unittest: DONE
        """ Initialize the VObject
        """
        logger.debug("VObject::Core.__init__")
        self.path = csys.strip_path_string(path)
        self.config_file = metadata.ConfigFile(self.path+"/.chern/config.json")
        logger.debug("VObject::Core.__init__ done")

    def __str__(self) -> str: # Unittest: DONE
        """ Define the behavior of print(vobject)
        """
        return self.invariant_path()

    def __repr__(self) -> str: # Unittest: DONE
        """ Define the behavior of print(vobject)
        """
        return self.invariant_path()

    # Path handling, type and status
    def invariant_path(self) -> str: # Unittest: DONE
        """ The path relative to the project root.
        It is invariant when the project is moved.
        """
        project_path = csys.project_path(self.path)
        path = os.path.relpath(self.path, project_path)
        return path

    def relative_path(self, path: str) -> str: # Unittest: DONE
        """ Return a path relative to the path of this object
        """
        return os.path.relpath(path, self.path)

    def object_type(self) -> str: # Unittest: DONE
        """ Return the type of the this object.
        """
        return self.config_file.read_variable("object_type", "")

    def is_task(self) -> bool: # Unittest: DONE
        """ Judge whether it is a task.
        """
        return self.object_type() == "task"

    def is_algorithm(self) -> bool: # Unittest: DONE
        """ Judge whether it is an algorithm.
        """
        return self.object_type() == "algorithm"

    def is_task_or_algorithm(self) -> bool: # Unittest: DONE
        """ Judge whether it is a task or an algorithm.
        """
        if self.object_type() == "task":
            return True
        if self.object_type() == "algorithm":
            return True
        return False

    def is_zombie(self) -> bool: # Unittest: DONE
        """ Judge whether it is actually an object
        """
        return self.object_type() == ""

    @abstractmethod
    def get_vobject(self, path: str) -> 'VObject':
        """ To avoid circular import
        """

    @abstractmethod
    def status(self, consult_id: Optional[int] = None) -> str:
        """ Abstract method for future implementation"""

    @abstractmethod
    def job_status(self, runner: Optional[str] = None) -> str:
        """ Abstract method for future implementation"""

    @abstractmethod
    def import_file(self, path: str) -> None:
        """ Abstract method for future implementation"""

    # Abstract methods, for file operations
    @abstractmethod
    def sub_objects_recursively(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def sub_objects(self):
        """ Abstract method for future implementation"""

    # Abstract methods, for arc management
    @abstractmethod
    def add_arc_from(self, obj):
        """ Abstract method for future implementation"""

    @abstractmethod
    def remove_arc_from(self, obj, single=False):
        """ Abstract method for future implementation"""

    @abstractmethod
    def add_arc_to(self, obj):
        """ Abstract method for future implementation"""

    @abstractmethod
    def remove_arc_to(self, obj, single=False):
        """ Abstract method for future implementation"""

    @abstractmethod
    def successors(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def predecessors(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def has_successor(self, obj):
        """ Abstract method for future implementation"""

    @abstractmethod
    def has_predecessor(self, obj):
        """ Abstract method for future implementation"""

    @abstractmethod
    def has_predecessor_recursively(self, obj):
        """ Abstract method for future implementation"""

    # Abstrac methods, for alias management
    @abstractmethod
    def path_to_alias(self, path):
        """ Abstract method for future implementation"""

    @abstractmethod
    def alias_to_path(self, alias):
        """ Abstract method for future implementation"""

    @abstractmethod
    def alias_to_impression(self, alias):
        """ Abstract method for future implementation"""

    @abstractmethod
    def has_alias(self, alias):
        """ Abstract method for future implementation"""

    @abstractmethod
    def remove_alias(self, alias):
        """ Abstract method for future implementation"""

    @abstractmethod
    def set_alias(self, alias, path):
        """ Abstract method for future implementation"""

    # Impression
    @abstractmethod
    def impress(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def impression(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def is_impressed_fast(self):
        """ Abstract method for future implementation"""

    # Other methods
    @abstractmethod
    def readme(self):
        """ Abstract method for future implementation"""

    @abstractmethod
    def color_tag(self, status):
        """ Abstract method for future implementation"""
