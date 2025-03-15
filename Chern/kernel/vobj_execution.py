from .ChernCache import ChernCache
from .ChernCommunicator import ChernCommunicator

from os.path import join
from ..utils import csys
from ..utils import utils

from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class ExecutionManagement:
    def is_submitted(self, machine="local"):
        """ Judge whether submitted or not. Return a True or False.
        [FIXME: incomplete]
        """
        if not self.is_impressed_fast():
            return False
        return False

    def submit(self, machine="local"):
        cherncc = ChernCommunicator.instance()
        self.deposit()
        cherncc.execute([self.impression().uuid], machine)

    def resubmit(self, machine="local"):
        if not self.is_submitted():
            print("Not submitted yet.")
            return
        cherncc = ChernCommunicator.instance()
        cherncc.resubmit(self.impression(), machine)
        path = join(
            utils.storage_path(),
            self.impression().uuid
        )
        csys.rm_tree(path)
        self.submit()

    def deposit(self):
        cherncc = ChernCommunicator.instance()
        if self.is_deposited():
            return
        if not self.is_impressed_fast():
            self.impress()
        for obj in self.predecessors():
            obj.deposit()
        cherncc.deposit(self.impression())

    def is_deposited(self):
        if not self.is_impressed_fast():
            return False
        cherncc = ChernCommunicator.instance()
        return cherncc.is_deposited(self.impression()) == "TRUE"
