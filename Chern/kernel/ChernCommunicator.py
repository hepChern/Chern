"""
Chern class for communicate to local and remote server.
"""

import tarfile
import os
import requests
from Chern.utils import csys
from Chern.utils import metadata
from logging import getLogger
logger = getLogger("ChernLogger")

class ChernCommunicator(object):
    ins = None
    def __init__(self):
        self.local_config_dir = csys.local_config_dir()
        project_path = csys.project_path()
        self.config_file = metadata.ConfigFile(project_path+"/.chern/hosts.json")

    @classmethod
    def instance(cls):
        if cls.ins is None:
            cls.ins = ChernCommunicator()
        return cls.ins

    def submit(self, impression, machine="local"):
        ## I should find a way to connect all the submission together to create a larger workflow
        tarname = impression.tarfile
        files = { "{}.tar.gz".format(impression.uuid) : open(tarname, "rb").read(), "config.json" : open(impression.path+"/config.json", "rb").read() }
        url = self.serverurl()
        machine_id = requests.get("http://{}/machine_id/{}".format(url, machine)).text
        requests.post("http://{}/upload".format(url), data = {'tarname': "{}.tar.gz".format(impression.uuid), 'config':"config.json"}, files = files)
        ## FIXME: here we simply assume that the upload is always correct
        requests.get("http://{}/run/{}/{}".format(url, impression.uuid, machine_id))

    def deposit(self, impression, machine="local"):
        ## I should find a way to connect all the submission together to create a larger workflow
        tarname = impression.tarfile
        files = { "{}.tar.gz".format(impression.uuid) : open(tarname, "rb").read(), "config.json" : open(impression.path+"/config.json", "rb").read() }
        url = self.serverurl()
        machine_id = requests.get("http://{}/machine_id/{}".format(url, machine)).text
        requests.post("http://{}/upload".format(url), data = {'tarname': "{}.tar.gz".format(impression.uuid), 'config':"config.json"}, files = files)
        ## FIXME: here we simply assume that the upload is always correct

    def execute(self, impressions, machine="local"):
        files = { "impressions" : " ".join(impressions) }
        url = self.serverurl()
        machine_id = requests.get("http://{}/machine_id/{}".format(url, machine)).text
        requests.post("http://{}/execute".format(url), data = {'machine': machine_id} , files = files)

    # This is to check the status of the impression on any machine
    def is_deposited(self, impression):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/deposited/{}".format(url, impression.uuid))
        except:
            return "FALSE"
        return r.text

    def workflow(self, impression, machine="local"):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/workflow/{}".format(url, impression.uuid))
        except:
            return "unconnected"
        return r.text.split()


    def resubmit(self, impression, machine="local"):
        # Well, I don't know how to do it.
        # Because we need to check which part has the problem, etc.
        # For testing purpose on a small project, we should first remove every thing in the impression and workflow directory and then to redo the submit
        pass

    def add_host(self, url):
        ## FIXME: add host_name and url check
        self.config_file.write_variable("serverrul", url)

    def serverurl(self):
        return self.config_file.read_variable("serverurl", "localhost:5000")

    # This is to check the status of the impression on any machine
    def status(self, impression):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/status/{}".format(url, impression.uuid))
        except:
            return "unconnected"
        return r.text

    def run_status(self, impression, machine="local"):
        url = self.serverurl()
        try:
            r = requests.get("http://{}/runstatus/{}/{}".format(url, impression.uuid, machine))
        except:
            return "unconnected"
        return r.text

    def register_machine(self, machine, machine_id):
        url = self.serverurl()
        r = requests.get("http://{}/register/{}/{}".format(url, machine, machine_id))

    def collect(self, impression):
        url = self.serverurl()
        r = requests.get("http://{}/collect/{}".format(url, impression.uuid))
        return r.text

    def host_status(self):
        logger.debug("ChernCommunicator/host_status")
        url = self.serverurl()
        logger.debug("url: {}".format(url))
        try:
            logger.debug("http://{}/serverstatus".format(url))
            r = requests.get("http://{}/serverstatus".format(url))
            logger.debug(r)
        except:
            return "unconnected"
        status = r.text
        if (status == "ok"):
            return "ok"
        return "unconnected"

    def output_files(self, impression, machine="local"):
        url = self.serverurl()
        machine_id = requests.get("http://{}/machine_id/{}".format(url, machine)).text
        r = requests.get("http://{}/outputs/{}/{}".format(url, impression, machine_id))
        return r.text.split()

    def get_file(self, impression, filename):
        url = self.serverurl()
        path = requests.get("http://{}/getfile/{}/{}".format(url, impression, filename)).text
        return path
