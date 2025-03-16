""" This module provides the ExecutionManagement class.
"""
from logging import getLogger
from os.path import join

from .ChernCommunicator import ChernCommunicator

from ..utils import csys

from .vobj_core import Core

logger = getLogger("ChernLogger")


class ExecutionManagement(Core):
    """ Manage the contact with dite and runner. """
    def is_submitted(self, runner="local"): # pylint: disable=unused-argument
        """ Judge whether submitted or not. Return a True or False.
        """
        # FIXME: incomplete
        if not self.is_impressed_fast():
            return False
        return False

    def submit(self, runner="local"):
        """ Submit the impression to the runner. """
        cherncc = ChernCommunicator.instance()
        self.deposit()
        cherncc.execute([self.impression().uuid], runner)

    def resubmit(self, runner="local"):
        """ Resubmit the impression to the runner. """
        # FIXME: incomplete

    def deposit(self):
        """ Deposit the impression to the dite. """
        cherncc = ChernCommunicator.instance()
        if self.is_deposited():
            return
        if not self.is_impressed_fast():
            self.impress()
        for obj in self.predecessors():
            obj.deposit()
        cherncc.deposit(self.impression())

    def is_deposited(self):
        """ Judge whether deposited or not. Return a True or False. """
        if not self.is_impressed_fast():
            return False
        cherncc = ChernCommunicator.instance()
        return cherncc.is_deposited(self.impression()) == "TRUE"
