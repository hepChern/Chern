"""
Chern class for communicate to local and remote server.
"""

import tarfile
import os
import requests
from Chern.utils import csys
from Chern.utils import metadata
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

    def submit(self, host, path, impression, readme=None):
        tarname = impression.tarfile
        files = { "{}.tar.gz".format(impression.uuid) : open(tarname, "rb").read() }
        url = self.url(host)
        requests.post("http://{}/upload".format(url), data = {'tarname': "{}.tar.gz".format(impression.uuid)}, files = files)


    def add_host(self, host, url):
        ## FIXME: add host_name and url check
        hosts = self.config_file.read_variable("hosts", [])
        urls = self.config_file.read_variable("urls", {})
        if (host not in urls):
            hosts.append(host)
        urls[host] = url
        self.config_file.write_variable("hosts", hosts)
        self.config_file.write_variable("urls", urls)

    def urls(self):
        return self.config_file.read_variable("urls", {})

    def hosts(self):
        return self.config_file.read_variable("hosts", [])

    def url(self, host):
        return self.urls().get(host, None)

    def status(self, host, impression):
        url = self.url(host)
        print("http://{}/status/{}".format(url, impression.uuid))
        try:
            r = requests.get("http://{}/status/{}".format(url, impression.uuid))
        except:
            return "unconnected"
        return r.text

    def run_status(self, host, impression):
        url = self.url(host)
        try:
            r = requests.get("http://{}/status/{}".format(url, impression.uuid))
        except:
            return "unconnected"
        return r.text


    def host_status(self, host):
        url = self.url(host)
        print(url)
        try:
            r = requests.get("http://{}/serverstatus".format(url))
            print(r.text)
        except:
            return "unconnected"
        status = r.text
        if (status == "ok"):
            return "ok"
        return "unconnected"

    def output_files(self, host, impression):
        url = self.url(host)
        r = requests.get("http://{}/outputs/{}".format(url, impression))
        return r.text.split()

    def get_file(self, host, impression, filename):
        url = self.url(host)
        r = requests.get("http://{}/getfile/{}/{}".format(url, impression, filename))
        return r.text
