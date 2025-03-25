""" This module provides the ExecutionManagement class.
"""
from logging import getLogger

from .chern_communicator import ChernCommunicator
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
        if not self.is_task_or_algorithm():
            sub_objects = self.sub_objects()
            for sub_object in sub_objects:
                sub_object.deposit()
            return

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

    def job_status(self, runner=None):
        """ Get the status of the job"""
        if not self.is_task_or_algorithm():
            sub_objects = self.sub_objects()
            pending = False
            for sub_object in sub_objects:
                status = sub_object.job_status()
                if status == "failed":
                    return "failed"
                if status != "finished":
                    pending = True
            if pending:
                return "pending"
            else:
                return "finished"
        cherncc = ChernCommunicator.instance()
        if runner is None:
            return cherncc.job_status(self.impression())
        return cherncc.job_status(self.impression(), runner)
