from Chern.kernel.VObject import VObject
from Chern.utils.utils import debug
from Chern.utils import utils
from Chern.utils import csys
import os
import subprocess
class VProject(VObject):

    def helpme(self, command):
        from Chern.kernel.Helpme import project_helpme
        print(project_helpme.get(command, "No such command, try ``helpme'' alone."))

def init_project():
    """ Create a new project from the existing folder
    """
    pwd = os.getcwd()
    if os.listdir(pwd) != []:
        raise Exception("Initialize on a unempty directory is not allowed")
    project_name = pwd[pwd.rfind("/")+1:]
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

    print("Your name and email is needed to initialize git.")
    user_name = input("Please input your name: ")
    user_mail = input("Please input your email: ")

    project_path = pwd
    config_file = utils.ConfigFile(project_path+"/.chern/config.py")
    config_file.write_variable("object_type", "project")
    with open(project_path + "/README.md", "w") as f:
        f.write("Please write README for this project")
    subprocess.call("vim %s/README.md"%project_path, shell=True)
    global_config_file = utils.ConfigFile(csys.local_config_path())
    projects_path = global_config_file.read_variable("projects_path")
    if projects_path is None:
        projects_path = {}
    projects_path[project_name] = project_path
    global_config_file.write_variable("projects_path", projects_path)
    global_config_file.write_variable("current_project", project_name)
    os.chdir(project_path)
    subprocess.call("git init", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call("git add .chern/config.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call("git commit -m \" Create config file for the project\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call("git add README.md", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call("git commit -m \" Create README file for the project\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

    ncpus = int(input("Please input the number of cpus to use for this project: "))
    user_name = input("Please input your name: ")
    user_mail = input("Please input your email: ")

    pwd = os.getcwd()
    project_path = pwd + "/" + project_name
    if not os.path.exists(project_path):
        os.mkdir(project_path)
    else:
        raise Exception("Project exist")
    config_file = utils.ConfigFile(project_path+"/.chern/config.py")
    config_file.write_variable("object_type", "project")
    config_file.write_variable("ncpus", ncpus)
    config_file.write_variable("user_name", user_name)
    config_file.write_variable("user_mail", user_mail)
    with open(project_path + "/README.md", "w") as f:
        f.write("Please write README for this project")
    call("vim %s/README.md"%project_path, shell=True)
    global_config_file = utils.ConfigFile(self.global_config_path)
    projects_path = global_config_file.read_variable("projects_path")
    if projects_path is None:
        projects_path = {}
    projects_path[project_name] = project_path
    global_config_file.write_variable("projects_path", projects_path)
    global_config_file.write_variable("current_project", project_name)
    os.chdir(project_path)
    call("git init", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    call("git add .chern/config.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    call("git commit -m \" Create config file for the project\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    call("git add README.md", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    call("git commit -m \" Create README file for the project\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

