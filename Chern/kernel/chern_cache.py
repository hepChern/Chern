# pylint: disable=too-few-public-methods
"""
This module is responsible for saving the cache
used by other parts of the application.
"""
from ..utils import csys

class ChernCache:
    """
    The class is the cache of the application.
    """
    ins = None  # Singleton instance

    def __init__(self):
        self.local_config_path = csys.local_config_path()
        self.consult_table = {}
        self.impression_consult_table = {}
        self.predecessor_consult_table = {}
        self.status_consult_table = {}

    @classmethod
    def instance(cls):
        """Returns the singleton instance of ChernCache."""
        if cls.ins is None:
            cls.ins = ChernCache()
        return cls.ins
