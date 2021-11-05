""" The helper class that is used to "operate" the project
    It is only used to "operate" things since all the information are stored in disk
    The core part may move to c language in the future
"""
import Chern
from Chern.kernel.VObject import VObject
from Chern.utils.utils import debug
from Chern.utils import utils
from Chern.utils import metadata
from Chern.utils import csys
import os
import subprocess
class VProject(VObject):

    def helpme(self, command):
        from Chern.kernel.Helpme import project_helpme
        print(project_helpme.get(command, "No such command, try ``helpme'' alone."))

    def submit(self):
        sub_objects = self.sub_objects()
        for sub_object in sub_objects:
            if sub_object.object_type() == "task":
                Chern.kernel.VTask.VTask(sub_object.path).submit()
            elif sub_object.object_type() == "algorithm":
                Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).submit()
            else:
                Chern.kernel.VDirectory.VDirectory(sub_object.path).submit()

    def status(self):
        sub_objects = self.sub_objects()
        for sub_object in sub_objects:
            if sub_object.object_type() == "task":
                if Chern.kernel.VTask.VTask(sub_object.path).status() != "done":
                    return "unfinished"
            elif sub_object.object_type() == "algorithm":
                if Chern.kernel.VAlgorithm.VAlgorithm(sub_object.path).status() != "built":
                    return "unfinished"
            elif Chern.kernel.VDirectory.VDirectory(sub_object.path).status() != "finished":
                return "unfinished"
        return "finished"


######################################
# Helper functions
def create_readme(project_path):
    open(project_path+"/.chern/project.json", "w").close()
    with open(project_path + "/.chern/README.md", "w") as f:
        f.write("Please write README for this project")
    # FIXME: should add a test whether vim is available
    subprocess.call("vim {}/.chern/README.md".format(project_path), shell=True)

def create_configfile(project_path, uuid):
    config_file = metadata.ConfigFile(project_path+"/.chern/config.json")
    config_file.write_variable("object_type", "project")
    config_file.write_variable("chern_version", "4.0.0")
    config_file.write_variable("project_uuid", uuid)





######################################
# Functions:

def init_project():
    """ Create a new project from the existing folder
    """
    pwd = os.getcwd()
    if os.listdir(pwd) != []:
        raise Exception("[ERROR] Initialize on a unempty directory is not allowed {}".format(pwd))
    project_name = pwd[pwd.rfind("/")+1:]
    print("The project name is ``{}'', would you like to change it? [y/n]".format(project_name))
    change = input()
    if change == "y":
        project_name = input("Please input the project name: ")

    # Check the forbidden name
    forbidden_names = ["config", "new", "projects", "start", "", "."]
    def check_project_failed(project_name, forbidden_names):
        message = "The following project names are forbidden:"
        message += "\n    "
        for name in forbidden_names:
            message += name + ", "
        raise Exception(message)
    if project_name in forbidden_names:
        check_project_failed(project_name, forbidden_names)

    project_path = pwd
    uuid = csys.generate_uuid()
    create_readme(project_path, uuid)
    global_config_file = metadata.ConfigFile(csys.local_config_path())
    projects_path = global_config_file.read_variable("projects_path", {})
    projects_path[project_name] = project_path
    global_config_file.write_variable("projects_path", projects_path)
    global_config_file.write_variable("current_project", project_name)
    os.chdir(project_path)

def use_project(path):
    """ Use an exsiting project
    """
    path = os.path.abspath(path)
    project_name = path[path.rfind("/")+1:]
    print("The project name is ``{}'', would you like to change it? [y/n]".format(project_name))
    change = input()
    if change == "y":
        project_name = input("Please input the project name")

    # Check the forbidden name
    forbidden_names = ["config", "new", "projects", "start", "", "."]
    def check_project_failed(project_name, forbidden_names):
        message = "The following project names are forbidden:"
        message += "\n    "
        for name in forbidden_names:
            message += name + ", "
        raise Exception(message)
    if project_name in forbidden_names:
        check_project_failed(project_name, forbidden_names)

    project_path = path
    uuid = csys.generate_uuid()
    config_file = utils.ConfigFile(project_path+"/.chern/config.json")
    object_type = config_file.read_variable("object_type", "")
    if object_type != "project":
        print("What!!?")
        return
    cwd = os.getcwd()
    os.chdir(path)
    project = VObject(path)
    print(path)
    global_config_file = metadata.ConfigFile(csys.local_config_path())
    projects_path = global_config_file.read_variable("projects_path", {})
    projects_path[project_name] = project_path
    print("Written")
    global_config_file.write_variable("projects_path", projects_path)
    global_config_file.write_variable("current_project", project_name)
    os.chdir(project_path)


def new_project(project_name):
    """ Create a new project
    """
    project_name = utils.strip_path_string(project_name)
    print("The project name is ", project_name)

    # Check the forbidden name
    forbidden_names = ["config", "new", "projects", "start"]
    def check_project_failed(project_name, forbidden_names):
        message = "The following project names are forbidden:"
        message += "\n    "
        for name in forbidden_names:
            message += name + ", "
        raise Exception(message)
    if project_name in forbidden_names:
        check_project_failed(project_name, forbidden_names)

    pwd = os.getcwd()
    project_path = pwd + "/" + project_name
    if not os.path.exists(project_path):
        os.mkdir(project_path)
    else:
        raise Exception("Project exist")
    uuid = csys.generate_uuid()
    create_configfile(project_path, uuid)
    create_readme(project_path)
    global_config_file = metadata.ConfigFile(csys.local_config_path())
    projects_path = global_config_file.read_variable("projects_path")
    if projects_path is None:
        projects_path = {}
    projects_path[project_name] = project_path
    global_config_file.write_variable("projects_path", projects_path)
    global_config_file.write_variable("current_project", project_name)
    os.chdir(project_path)

