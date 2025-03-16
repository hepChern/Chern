""" JobManager class for managing tasks
"""
from logging import getLogger

from .ChernCommunicator import ChernCommunicator
from .vtask_core import Core

logger = getLogger("ChernLogger")

class JobManager(Core):
    """ JobManager class for managing tasks"""

    def kill(self):
        """ Kill the task
        """
        cherncc = ChernCommunicator.instance()
        cherncc.kill(self.impression())

    def job_status(self, host=None):
        """ Get the status of the job"""
        cherncc = ChernCommunicator.instance()
        if host is None:
            return cherncc.job_status(self.impression())
        return cherncc.job_status(self.impression(), host)

    def run_status(self, host="local"): # pylint: disable=unused-argument
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

    def export(self, filename, output_file):
        """ Export the file"""
        cherncc = ChernCommunicator.instance()
        output_file_path = cherncc.export(
            self.impression(), filename, output_file
            )
        if output_file_path == "NOTFOUND":
            print(f"File {filename} not found")

    def send_data(self, path):
        """ Send data to the job"""
        cherncc = ChernCommunicator.instance()
        cherncc.deposit_with_data(self.impression(), path)
