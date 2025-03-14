from .ChernCommunicator import ChernCommunicator

from logging import getLogger
logger = getLogger("ChernLogger")


class JobManager:
    # Submission Methods
    def kill(self):
        """
        Kill the task
        """
        cherncc = ChernCommunicator.instance()
        cherncc.kill(self.impression())

    # Status Checking Methods
    def run_status(self, host="local"):
        cherncc = ChernCommunicator.instance()
        environment = self.environment()
        if environment == "rawdata":
            md5 = self.input_md5()
            dite_md5 = cherncc.sample_status(self.impression())
            if dite_md5 == md5:
                return "finished"
            else:
                return "unsubmitted"
        return cherncc.status(self.impression())

    # Communicator Interaction Methods
    def collect(self):
        cherncc = ChernCommunicator.instance()
        cherncc.collect(self.impression())

    def display(self, filename):
        cherncc = ChernCommunicator.instance()
        # Open the browser to display the file
        cherncc.display(self.impression(), filename)

    def export(self, filename, output_file):
        cherncc = ChernCommunicator.instance()
        output_file_path = cherncc.export(
            self.impression(), filename, output_file
            )
        if output_file_path == "NOTFOUND":
            print("File {} not found".format(filename))
            return
