""" JobManager class for managing tasks
"""
import os
from logging import getLogger

from .chern_communicator import ChernCommunicator
from ..utils import csys
from .vtask_core import Core

logger = getLogger("ChernLogger")

class JobManager(Core):
    """ JobManager class for managing tasks"""

    def kill(self):
        """ Kill the task
        """
        cherncc = ChernCommunicator.instance()
        cherncc.kill(self.impression())

    def run_status(self, runner="none"): # pylint: disable=unused-argument
        """ Get the run status of the job"""
        # FIXME duplicated code
        cherncc = ChernCommunicator.instance()
        environment = self.environment()
        if environment == "rawdata":
            md5 = self.input_md5()
            dite_md5 = cherncc.sample_status(self.impression())
            if dite_md5 == md5:
                return "finished"
            return "unsubmitted"
        return cherncc.status(self.impression())

    # Communicator Interaction Methods
    def collect(self):
        """ Collect the results of the job"""
        cherncc = ChernCommunicator.instance()
        cherncc.collect(self.impression())

    def display(self, filename):
        """ Display the file"""
        cherncc = ChernCommunicator.instance()
        # Open the browser to display the file
        cherncc.display(self.impression(), filename)

    def impview(self):
        """ Open browser to view the impression"""
        cherncc = ChernCommunicator.instance()
        cherncc.impview(self.impression())

    def export(self, filename, output_file):
        """ Export the file"""
        cherncc = ChernCommunicator.instance()
        output_file_path = cherncc.export(
            self.impression(), filename, output_file
            )
        if output_file_path == "NOTFOUND":
            logger.error(
                "File %s not found in the job %s",
                filename, self.impression()
            )

    def send_data(self, path):
        """ Send data to the job"""
        cherncc = ChernCommunicator.instance()
        cherncc.deposit_with_data(self.impression(), path)

    def workaround_preshell(self) -> (tuple[bool, str]):
        """ Pre-shell workaround"""
        cherncc = ChernCommunicator.instance()
        status = cherncc.dite_status()
        if status != "connected":
            return (False, "")
        # make a temporal directory for data deposit
        temp_dir = csys.create_temp_dir(prefix="chernws_")
        # copy the data to the temporal directory
        file_list = csys.tree_excluded(self.path)
        for dirpath, _, filenames in file_list:
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                rel_path = os.path.relpath(full_path, self.path)
                dest_path = os.path.join(temp_dir, rel_path)
                csys.copy(full_path, dest_path)
        return (True, temp_dir)

    def workaround_postshell(self) -> bool:
        """ Post-shell workaround"""
        return True
