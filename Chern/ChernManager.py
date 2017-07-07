import os
from Chern import utils
from Chern.VAlgorithm import VAlgorithm
from Chern.VTask import VTask
from Chern.VData import VData
from Chern.VDirectory import VDirectory
from Chern.VProject import VProject

VObjectClass = {"algorithm":VAlgorithm, "task":VTask, "data":VData, "directory":VDirectory, "project":VProject}

class ChernManager(object):
    instance = None

    @classmethod
    def get_manager(self):
        if self.instance == None:
            self.instance = ChernManager()
        return self.instance

    def __init__(self):
        print("this is to time the instance time")
        self.c = None
        self.p = None
        self.init_global_config()

    def create_object_instance(self, path):
        path = utils.strip_path_string(path)
        object_config_file = utils.ConfigFile(path+"/.config.py")
        object_type = object_config_file.read_variable("object_type")
        print(object_type)
        return VObjectClass[object_type](path)

    def init_global_config(self):
        chern_config_path = os.environ.get("CHERNCONFIGPATH")
        if chern_config_path == None:
            raise Exception("CHERNCONFIGPATH is not set")
        self.global_config_path = utils.strip_path_string(chern_config_path) + "/config.py"

    def get_current_project(self):
        """ Get the name of the current working project.
        If there isn't a working project, return "/"
        """
        global_config_file = utils.ConfigFile(self.global_config_path)
        current_project = global_config_file.read_variable("current_project")
        return current_project

    def get_all_projects(self):
        """ Get the list of all the projects.
        If there is not a list create one.
        """
        global_config_file = utils.ConfigFile(self.global_config_path)
        projects_path = global_config_file.read_variable("projects_path")
        return projects_path.keys()

    def ls_projects(self):
        """
        ls projects
        """
        projects_list = self.get_all_projects()
        for project_name in projects_list:
            print(project_name)

    def get_project_path(self, project_name):
        """ Get The path of a specific project.
        You must be sure that the project exists.
        This function don't check it.
        """
        global_config_file = utils.ConfigFile(self.global_config_path)
        projects_path = global_config_file.read_variable("projects_path")
        return projects_path[project_name]


    def switch_project(project_name):
        global global_config_path
        global_config = utils.get_global_config()
        utils.write_variables(global_config, global_config_path, [("current_project", project_name)])
        global global_vproject
        del global_vproject
        global_vproject = VProject()


    def new_project(project_name):
        project_name = utils.strip(project_name)

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

        pwd = os.getcwd()
        if not os.path.exists(pwd + "/" + project_name):
            os.mkdir(pwd + "/" + project_name)
        else:
            raise Exception("Project exist")
        global_config = utils.get_global_config()
        projects_path = global_config.projects_path if "projects_path" in dir(global_config) else {}
        projects_path[project_name] = pwd + "/" + project_name
        utils.write_variables(global_config, global_config_path, [("projects_path", projects_path)])

        with open(pwd+"/"+project_name+"/.type", "w") as type_file:
            type_file.write("project")
        global global_vproject
        global_vproject = VProject(pwd+"/"+project_name, None)

        def update_configuration():
            if not os.path.exists(global_config_path):
                shutil.copyfile(os.environ["CHENSYSPATH"]+"/config/global_config.py", os.environ["HOME"])

        def main(command_list):
            #current_project = get_current_project()
            #projects_list = get_all_projects()

            if len(command_list) == 0 :
                # print "Current project is:", get_current_project()
                # print "All the projects are:",
                for obj in get_all_projects():
                    pass
                    # print obj,
                return

            if command_list[0] == "config":
                update_configuration()
                from subprocess import call
                call("vim " + get_project_path(get_current_project()) + "/.config/config.py", shell = True)
                return

            if not command_list[0] in get_all_projects():
                print("No such a project ", command_list[0], " try to create a new one.")
                #try:
                new_project(command_list[0])
                #except Exception as e:
                #    print e

            if command_list[0] in get_all_projects():
                switch_project(command_list[0])
                print("Switch to project", command_list[0])
                return "cd " + get_project_path(command_list[0]) + "\n"

            #except :
            #    print "Can not config new project for some reason"


def get_manager():
    return ChernManager.get_manager()
