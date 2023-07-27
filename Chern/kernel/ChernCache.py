"""
  
"""
import sys
import os
import subprocess
from Chern.utils import csys
from Chern.utils import metadata

class ChernCache(object):
    ins = None
    def __init__(self):
        self.local_config_path = csys.local_config_path()
        self.consult_table = {}
        self.impression_consult_table = {}
        self.status_consult_table = {}

    @classmethod
    def instance(cls):
        if cls.ins is None:
            cls.ins = ChernCache()
        return cls.ins
