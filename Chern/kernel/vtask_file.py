from logging import getLogger

from Chern.kernel import VAlgorithm
from ..utils import metadata
from ..utils import csys
from .ChernCommunicator import ChernCommunicator
form .vtask_core import Core

from os.path import join
logger = getLogger("ChernLogger")


class FileManager(Core):
    def cp(self, source, dst):
        if source.startswith("local:"):
            path = self.container().path+"/output/"+source.replace("local:", "").lstrip()
            if not csys.exists(path):
                print("File: {} do not exists".format(path))
                return
            csys.copy(path, dst)

    def importfile(self, filename):
        """
        Import the file to this task directory
        """
        csys.copy(filename, self.path)

    def input_md5(self):
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        return parameters_file.read_variable("uuid", "")

    def set_input_md5(self, path):
        md5 = csys.dir_md5(path)
        parameters_file = metadata.YamlFile(join(self.path, "chern.yaml"))
        parameters_file.write_variable("uuid", md5)
        return md5

    def stdout(self):
        with open(self.container().path+"/stdout") as f:
            return f.read()

    def stderr(self):
        with open(self.container().path+"/stderr") as f:
            return f.read()

    def output_md5(self):
        output_md5s = self.config_file.read_variable("output_md5s", {})
        return output_md5s.get(self.impression(), "")
