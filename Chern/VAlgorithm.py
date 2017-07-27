from Chern.VObject import VObject
from Chern import utils
import os
import subprocess
class VAlgorithm(VObject):
    def __init__(self, file_name):
        super(VAlgorithm, self).__init__(file_name)

    def ls(self):
        """
        Option to
        """
        super(VAlgorithm, self).ls()



def create_algorithm(path, inloop=False):
    path = utils.strip_path_string(path)
    os.mkdir(path)
    with open(path + "/.config.py", "w") as f:
        f.write("object_type = \"algorithm\"\n")
        f.write("main_file = \"main.py\"\n")
    with open(path + "/.README.md", "w") as f:
        f.write("Please write README for this algorithm")
    subprocess.call("vim %s/.README.md"%path, shell=True)
    with open(path + "/main.py", "w") as f:
        f.write("Please write the main file for this algorithm")
    subprocess.call("vim %s/main.py"%path, shell=True)

