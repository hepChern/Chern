"""
Chern class for communicate to local and remote server.
"""

import tarfile
import subprocess
import requests
from ..utils import csys
from ..utils import metadata
from ..utils.pretty import colorize
from os.path import join
from logging import getLogger
logger = getLogger("ChernLogger")


class ChernCommunicator(object):
    ins = None

    # Initialization and Singleton
    def __init__(self):
        self.local_config_dir = csys.local_config_dir()
        project_path = csys.project_path()
        self.config_file = metadata.ConfigFile(
            join(project_path, ".chern/hosts.json")
            )

    @classmethod
    def instance(cls):
        if cls.ins is None:
            cls.ins = ChernCommunicator()
        return cls.ins

    # Submission and Execution
    def submit(self, impression, machine="local"):
        # I should find a way to connect all the submission
        # together to create a larger workflow
        tarname = impression.tarfile
        files = {
            "{}.tar.gz".format(impression.uuid): open(tarname, "rb").read(),
            "config.json": open(impression.path + "/config.json", "rb").read()
        }
        url = self.serverurl()
        machine_id = requests.get(
            "http://{}/machine_id/{}".format(url, machine)
        ).text
        requests.post(
            "http://{}/upload".format(url),
            data={
                'tarname': "{}.tar.gz".format(impression.uuid),
                'config': "config.json"
            },
            files=files
        )
        # FIXME: here we simply assume that the upload is always correct
        requests.get(
            "http://{}/run/{}/{}".format(url, impression.uuid, machine_id)
        )

    def deposit(self, impression):
        # I should find a way to connect all the submission
        # together to create a larger workflow
        tarname = impression.tarfile
        files = {
            "{}.tar.gz".format(impression.uuid): open(tarname, "rb").read(),
            "config.json": open(impression.path + "/config.json", "rb").read()
        }
        url = self.serverurl()
        requests.post(
            "http://{}/upload".format(url),
            data={
                'tarname': "{}.tar.gz".format(impression.uuid),
                'config': "config.json"
            },
            files=files
        )

    def execute(self, impressions, machine="local"):
        files = {"impressions": " ".join(impressions)}
        url = self.serverurl()
        machine_id = requests.get(
            "http://{}/machine_id/{}".format(url, machine)
        ).text
        requests.post(
            "http://{}/execute".format(url),
            data={'machine': machine_id},
            files=files
        )

    # This is to check the status of the impression on any machine
    def is_deposited(self, impression):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/deposited/{}".format(url, impression.uuid)
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "FALSE"
        return r.text

    def kill(self, impression):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/kill/{}".format(url, impression.uuid)
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected"
        return r.text

    def runners(self):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/runners".format(url))
        except Exception as e:
            return ["unconnected to DITE"]
        return r.text.split()

    def runners_url(self):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/runnersurl".format(url))
        except Exception as e:
            return ["unconnected to DITE"]
        return r.text.split()

    def register_runner(self, runner, runner_url, secret):
        url = self.serverurl()

        requests.post(
            "http://{}/registerrunner".format(url),
            data={'runner': runner, 'url': runner_url, 'secret': secret}
        )

    def remove_runner(self, runner):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/removerunner/{}".format(url, runner))
            if r.text != "successful":
                print("Failed to remove runner")
        except Exception as e:
            return ["unconnected to DITE"]
        return r.text.split()




    def workflow(self, impression, machine="local"):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/workflow/{}".format(url, impression.uuid)
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return ["unconnected to DITE"]
        return r.text.split()

    def sample_status(self, impression):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/samplestatus/{}".format(url, impression.uuid)
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected to DITE"
        return r.text

    def job_status(self, impression):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/status/{}".format(url, impression.uuid)
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected to DITE"
        return r.text

    def runner_connection(self, runner):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/runnerconnection/{}".format(url, runner)
            )
        except Exception as e:
            return "unconnected to DITE"
        return r.text

    def resubmit(self, impression, machine="local"):
        # Well, I don't know how to do it.
        # Because we need to check which part has the problem, etc.
        # For testing purpose on a small project,
        # we should first remove every thing in the impression
        # and workflow directory and then to redo the submit
        pass

    def add_host(self, url):
        # FIXME: add host_name and url check
        self.config_file.write_variable("serverurl", url)

    def serverurl(self):
        return self.config_file.read_variable("serverurl", "localhost:5000")

    # This is to check the status of the impression on any machine
    def status(self, impression):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/status/{}".format(url, impression.uuid)
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected"
        return r.text

    def run_status(self, impression, machine="local"):
        url = self.serverurl()
        try:
            r = requests.get(
                "http://{}/runstatus/{}/{}".format(
                    url, impression.uuid, machine
                )
            )
        except Exception as e:
            # Handle the exception here
            # print(f"An error occurred: {e}")
            return "unconnected"
        return r.text

    def collect(self, impression):
        url = self.serverurl()
        r = requests.get("http://{}/collect/{}".format(url, impression.uuid))
        return r.text

    def display(self, impression, filename, machine="local"):
        # Open the browser to display the file
        url = self.serverurl()
        # The browser is 'open'
        subprocess.call(["open", "http://{}/export/{}/{}".format(
            url, impression.uuid, filename
        )])

    def export(self, impression, filename, output, machine="local"):
        url = self.serverurl()
        requests.get("http://{}/machine_id/{}".format(
            url, machine)).text
        r = requests.get("http://{}/export/{}/{}".format(
            url, impression.uuid, filename
        ))
        # What we get is the file, save the file to the output
        with open(output, "wb") as f:
            f.write(r.content)

    def dite_status(self):
        logger.debug("ChernCommunicator/dite_status")
        url = self.serverurl()
        logger.debug("url: {}".format(url))
        try:
            logger.debug("http://{}/ditestatus".format(url))
            r = requests.get("http://{}/ditestatus".format(url))
            logger.debug(r)
        except Exception as e:
            return "unconnected"
        status = r.text
        if (status == "ok"):
            return "ok"
        return "unconnected"

    def dite_info(self):
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
        url = self.serverurl()
        if machine == "none":
            machine_id = "none"
        else:
            machine_id = requests.get(
                "http://{}/machine_id/{}".format(url, machine)
            ).text
        r = requests.get(
            "http://{}/outputs/{}/{}".format(url, impression, machine_id)
        )
        return r.text.split()

    def get_file(self, impression, filename):
        url = self.serverurl()
        path = requests.get(
            "http://{}/getfile/{}/{}".format(url, impression, filename)
        ).text
        return path

    def deposit_with_data(self, impression, path):
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
            "{}.tar.gz".format(impression.uuid): open(tarname, "rb").read(),
            "config.json": open(impression.path + "/config.json", "rb").read()
        }
        url = self.serverurl()

        requests.post(
            "http://{}/upload".format(url),
            data={
                'tarname': "{}.tar.gz".format(impression.uuid),
                'config': "config.json"
            },
            files=files
        )

# Deleted
#    def set_sample_uuid(self, impression, sample_uuid):
#        url = self.serverurl()
#        requests.get(
#            "http://{}/setsampleuuid/{}/{}".format(
#                url, impression.uuid, sample_uuid
#            )
#        )
