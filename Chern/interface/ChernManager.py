"""
This is the top class for project manager
"""
import os
from subprocess import call, PIPE
from Chern.utils import metadata
from Chern.utils import csys
import Chern.kernel.valgorithm as valg #as _VAlgorithm
import Chern.kernel.vtask as vtsk #as _VTask
import Chern.kernel.VDirectory as vdir
import Chern.kernel.VProject as vproj

def create_object_instance(path):
    """ Create an object instance
    """
    path = csys.strip_path_string(path)
    object_config_file = metadata.ConfigFile(path+"/.chern/config.json")
    object_type = object_config_file.read_variable("object_type")
    vobject_class = {"algorithm":valg.VAlgorithm,
                     "task":vtsk.VTask,
                     "directory":vdir.VDirectory,
                     "project":vproj.VProject}
    return vobject_class[object_type](path)

class ChernProjectManager(object):
    """ ChernManager class
    """
    instance = None
    c = None

    @classmethod
    def get_manager(cls):
        """ Return the manager itself
        """
        if cls.instance is None:
            cls.instance = ChernProjectManager()
        return cls.instance

    def __init__(self):
        self.init_global_config()

    def init_global_config(self):
        chern_config_path = os.environ.get("HOME") +"/.Chern"
        if not os.path.exists(chern_config_path):
            os.mkdir(chern_config_path)
        self.global_config_path = csys.strip_path_string(chern_config_path) + "/config.json"

    def get_current_project(self):
        """ Get the name of the current working project.
        If there isn't a working project, return None
        """
        global_config_file = metadata.ConfigFile(self.global_config_path)
        current_project = global_config_file.read_variable("current_project")
        if current_project is None:
            return None
        else:
            projects_path = global_config_file.read_variable("projects_path")
            path = projects_path.get(current_project, "no_place|")
            if path == "no_place|":
                projects_path[current_project] = "no_place|"
            if not os.path.exists(path):
                projects_path.pop(current_project)
                if projects_path != {}:
                    current_project = list(projects_path.keys())[0]
                else:
                    current_project = None
                global_config_file.write_variable("current_project", current_project)
                global_config_file.write_variable("projects_path", projects_path)
                return self.get_current_project()
            else:
                return current_project

    def get_all_projects(self):
        """ Get the list of all the projects.
        If there is not a list create one.
        """
        global_config_file = metadata.ConfigFile(self.global_config_path)
        projects_path = global_config_file.read_variable("projects_path")
        return list(projects_path.keys())

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
        global_config_file = metadata.ConfigFile(self.global_config_path)
        projects_path = global_config_file.read_variable("projects_path")
        return projects_path[project_name]

    def switch_project(self, project_name):
        """ Switch the current project

        """
        projects_list = self.get_all_projects()
        if project_name not in projects_list:
            print("No such a project")
            return
        global_config_file = metadata.ConfigFile(self.global_config_path)
        global_config_file.write_variable("current_project", project_name)
        path = self.get_project_path(project_name)
        if not os.path.exists(path):
            print("Project deleted")
            return
        self.c = create_object_instance(path)

    def switch_current_object(self, path):
        self.c = create_object_instance(path)

    def current_object(self):
        path = os.getcwd()
        return create_object_instance(path)


def get_manager():
    return ChernProjectManager.get_manager()
