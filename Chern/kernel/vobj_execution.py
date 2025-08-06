""" This module provides the ExecutionManagement class.
"""
from logging import getLogger
from typing import Optional, TYPE_CHECKING

from ..utils.message import Message
from .chern_communicator import ChernCommunicator
from .vobj_core import Core

if TYPE_CHECKING:
    from .vobject import VObject
    from .vimpression import VImpression

logger = getLogger("ChernLogger")


class ExecutionManagement(Core):
    """ Manage the contact with dite and runner. """
    def is_submitted(self, runner: str = "local") -> bool: # pylint: disable=unused-argument
        """ Judge whether submitted or not. Return a True or False.
        """
        # FIXME: incomplete
        if not self.is_impressed_fast():
            return False
        return False

    def submit(self, runner: str = "local") -> Message:
        """ Submit the impression to the runner. """
        cherncc = ChernCommunicator.instance()
        # Check the connection
        dite_status = cherncc.dite_status()
        if dite_status != "connected":
            msg = Message()
            msg.add("DITE is not connected. Please check the connection.", "warning")
            # logger.error(msg)
            return msg
        self.deposit()
        cherncc.execute([self.impression().uuid], runner)
        msg = Message()
        msg.add(f"Impression {self.impression().uuid} submitted to {runner}.")
        logger.info(msg)
        return msg

    def resubmit(self, runner: str = "local") -> None:
        """ Resubmit the impression to the runner. """
        # FIXME: incomplete

    def deposit(self) -> None:
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

    def is_deposited(self) -> bool:
        """ Judge whether deposited or not. Return a True or False. """
        if not self.is_impressed_fast():
            return False
        cherncc = ChernCommunicator.instance()
        return cherncc.is_deposited(self.impression()) == "TRUE"

    def job_status(self, runner: Optional[str] = None) -> str:
        """ Get the status of the job"""
        if not self.is_task_or_algorithm():
            sub_objects = self.sub_objects()
            pending = False
            for sub_object in sub_objects:
                status = sub_object.job_status()
                if status == "failed":
                    return "failed"
                if status not in ("finished", "archived"):
                    pending = True
            if pending:
                return "pending"
            return "finished"
        cherncc = ChernCommunicator.instance()
        if runner is None:
            return cherncc.job_status(self.impression())
        return cherncc.job_status(self.impression(), runner)
