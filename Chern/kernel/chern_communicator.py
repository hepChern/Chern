# pylint: disable=broad-exception-caught
# pylint: disable=too-many-public-methods
# pylint: disable=consider-using-with
"""
Chern class for communicate to local and remote server.
"""

from os.path import join
import json
from logging import getLogger
import subprocess
import tarfile
import requests

from ..utils import csys
from ..utils import metadata
from ..utils.pretty import colorize
logger = getLogger("ChernLogger")


class ChernCommunicator():
    """ Communicator for Chern """
    ins = None

    def __init__(self):
        """ Initialize the communicator and Singleton """
        self.local_config_dir = csys.local_config_dir()
        self.timeout = 10
        project_path = csys.project_path()
        self.config_file = metadata.ConfigFile(
            join(project_path, ".chern/hosts.json")
            )

    @classmethod
    def instance(cls):
        """ Singleton instance """
        if cls.ins is None:
            cls.ins = ChernCommunicator()
        return cls.ins

    # Submission and Execution
    def submit(self, impression, machine="local"):
        """ Submit the impression to the server """
        # I should find a way to connect all the submission
        # together to create a larger workflow
        tarname = impression.tarfile
        files = {
            f"{impression.uuid}.tar.gz": open(tarname, "rb").read(),
            "config.json": open(impression.path + "/config.json", "rb").read()
        }
        url = self.serverurl()
        machine_id = requests.get(
            f"http://{url}/machine_id/{machine}",
            timeout=self.timeout
        ).text
        requests.post(
            f"http://{url}/upload",
            data={
                'tarname': f"{impression.uuid}.tar.gz",
                'config': "config.json"
            },
            files=files,
            timeout=self.timeout
        )
        # FIXME: here we simply assume that the upload is always correct
        requests.get(
            f"http://{url}/run/{impression.uuid}/{machine_id}",
            timeout=self.timeout
        )

    def deposit(self, impression):
        """ Deposit the impression to the server """
        # I should find a way to connect all the submission
        # together to create a larger workflow
        tarname = impression.tarfile
        files = {
            f"{impression.uuid}.tar.gz": open(tarname, "rb").read(),
            "config.json": open(impression.path + "/config.json", "rb").read()
        }
        url = self.serverurl()
        requests.post(
            f"http://{url}/upload",
            data={
                'tarname': f"{impression.uuid}.tar.gz",
                'config': "config.json"
            },
            files=files,
            timeout=self.timeout
        )

    def execute(self, impressions, machine="local"):
        """ Execute the impressions on the server """
        files = {"impressions": " ".join(impressions)}
        url = self.serverurl()
        machine_id = requests.get(
            f"http://{url}/machine_id/{machine}",
            timeout=self.timeout
        ).text
        requests.post(
            f"http://{url}/execute",
            data={'machine': machine_id},
            files=files,
            timeout=self.timeout
        )

    # This is to check the status of the impression on any machine
    def is_deposited(self, impression):
        """ Check if the impression is deposited on the server """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/deposited/{impression.uuid}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return "FALSE"
        return r.text

    def kill(self, impression):
        """ Kill the impression on the server """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/kill/{impression.uuid}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected"
        return r.text

    def runners(self):
        """ Get the list of runners """
        url = self.serverurl()
        try:
            r = requests.get(
                    f"http://{url}/runners",
                    timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return ["unconnected to DITE"]
        return r.text.split()

    def runners_url(self):
        """ Get the list of runners """
        url = self.serverurl()
        try:
            r = requests.get(
                    f"http://{url}/runnersurl",
                    timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return ["unconnected to DITE"]
        return r.text.split()

    def register_runner(self, runner, runner_url, token):
        """ Register a runner to the server """
        url = self.serverurl()

        requests.post(
            f"http://{url}/registerrunner",
            data={'runner': runner, 'url': runner_url, 'token': token},
            timeout=self.timeout
        )

    def remove_runner(self, runner):
        """ Remove a runner from the server """
        url = self.serverurl()
        try:
            r = requests.get(
                    f"http://{url}/removerunner/{runner}",
                    timeout=self.timeout
            )
            if r.text != "successful":
                print("Failed to remove runner")
        except Exception as e:
            print(f"An error occurred: {e}")
            return ["unconnected to DITE"]
        return r.text.split()

    def workflow(self, impression):
        """ Get the workflow of the impression """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/workflow/{impression.uuid}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return ["unconnected to DITE"]
        return r.text.split()

    def sample_status(self, impression):
        """ Get the sample status of the impression """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/samplestatus/{impression.uuid}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return "unconnected to DITE"
        return r.text

    def job_status(self, impression):
        """ Get the job status of the impression """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/status/{impression.uuid}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected to DITE"
        return r.text

    def runner_connection(self, runner):
        """ Get the connection status of the runner """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/runnerconnection/{runner}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return "unconnected to DITE"
        return json.loads(r.text)

    def resubmit(self, impression, machine="local"):
        """ Resubmit the impression to the server """
        # Well, I don't know how to do it.
        # Because we need to check which part has the problem, etc.
        # For testing purpose on a small project,
        # we should first remove every thing in the impression
        # and workflow directory and then to redo the submit

    def add_host(self, url):
        """ Add a host to the server """
        # FIXME: add host_name and url check
        self.config_file.write_variable("serverurl", url)

    def serverurl(self):
        """ Get the serverurl """
        return self.config_file.read_variable("serverurl", "localhost:5000")

    # This is to check the status of the impression on any machine
    def status(self, impression):
        """ Get the status of the impression """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/status/{impression.uuid}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected"
        return r.text

    def run_status(self, impression, machine="local"):
        """ Get the run status of the impression """
        url = self.serverurl()
        try:
            r = requests.get(
                f"http://{url}/runstatus/{impression.uuid}/{machine}",
                timeout=self.timeout
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected"
        return r.text

    def collect(self, impression):
        """ Collect the impression from the server """
        url = self.serverurl()
        r = requests.get(
                f"http://{url}/collect/{impression.uuid}",
                timeout=self.timeout
        )
        return r.text

    def display(self, impression, filename):
        """ Display the file in the browser """
        # Open the browser to display the file
        url = self.serverurl()
        # The browser is 'open'
        subprocess.call(["open", f"http://{url}/export/{impression.uuid}/{filename}"
            ])

    def export(self, impression, filename, output):
        """ Export the file from the server """
        url = self.serverurl()
        # requests.get(
        #         f"http://{url}/machine_id/{machine}",
        #         timeout=self.timeout
        # ).text
        r = requests.get(
                f"http://{url}/export/{impression.uuid}/{filename}",
                timeout=self.timeout
        )
        # What we get is the file, save the file to the output
        with open(output, "wb") as f:
            f.write(r.content)

    def dite_status(self):
        """ Get the status of the DITE """
        logger.debug("ChernCommunicator/dite_status")
        url = self.serverurl()
        logger.debug("url: %s", url)
        try:
            logger.debug("http://%s/ditestatus", url)
            r = requests.get(f"http://{url}/ditestatus", timeout=self.timeout)
            logger.debug(r)
        except Exception as e:
            print(f"An error occurred: {e}")
            return "unconnected"
        status = r.text
        if status == "ok":
            return "ok"
        return "unconnected"

    def dite_info(self):
        """ Get the information of the DITE """
        w = ""
        w += colorize("DITE URL: ", "title0")
        w += colorize(self.serverurl(), "normal")
        w += "\n"
        w += colorize("DITE Status: ", "title0")
        if self.dite_status() == "ok":
            w += colorize("[connected]", "success")
        else:
            w += colorize("[unconnected]", "warning")
        w += "\n"
        return w

    def output_files(self, impression, machine="local"):
        """ Get the output files of the impression """
        url = self.serverurl()
        if machine == "none":
            machine_id = "none"
        else:
            machine_id = requests.get(
                f"http://{url}/machine_id/{machine}",
                timeout=self.timeout
            ).text
        r = requests.get(
            f"http://{url}/outputs/{impression}/{machine_id}",
            timeout=self.timeout
        )
        return r.text.split()

    def get_file(self, impression, filename):
        """ Get the file from the server """
        url = self.serverurl()
        path = requests.get(
            f"http://{url}/getfile/{impression}/{filename}",
            timeout=self.timeout
        ).text
        return path

    def deposit_with_data(self, impression, path):
        """ Deposit the impression with additional data """
        tmpdir = "/tmp"
        tarname = tmpdir + "/" + impression.uuid + ".tar.gz"
        impression_tar = tarfile.open(impression.tarfile, "r")
        # Add additional data to the tar file
        tar = tarfile.open(tarname, "w:gz")
        for member in impression_tar.getmembers():
            tar.addfile(member, impression_tar.extractfile(member))
        tar.add(path, arcname="rawdata")
        tar.close()
        impression_tar.close()

        files = {
            f"{impression.uuid}.tar.gz": open(tarname, "rb").read(),
            "config.json": open(impression.path + "/config.json", "rb").read()
        }
        url = self.serverurl()

        requests.post(
            f"http://{url}/upload",
            data={
                'tarname': f"{impression.uuid}.tar.gz",
                'config': "config.json"
            },
            files=files,
            timeout=self.timeout
        )
        requests.get(
                f"http://{url}/setjobstatus/{impression.uuid}/archived",
                timeout=self.timeout
        )
