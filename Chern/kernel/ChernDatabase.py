"""
  
"""
import sys
import os
import subprocess
from Chern.utils import csys
from Chern.utils import metadata
# from Chern.kernel.VJob import VJob
# from Chern.kernel.VContainer import VContainer
# from Chern.kernel.VImage import VImage

class ChernDatabase(object):
    ins = None
    def __init__(self):
        self.local_config_path = csys.local_config_path()
        self.consult_table = {}
        self.impression_consult_table = {}
        self.status_consult_table = {}

    @classmethod
    def instance(cls):
        if cls.ins is None:
            cls.ins = ChernDatabase()
        return cls.ins

    def is_docker_started(self):
        ps = subprocess.Popen("docker ps", shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ps.wait()
        return (ps.poll() == 0)

    """
    def job(self, id):
        storage_path = csys.storage_path()
        if os.path.exists(storage_path+"/"+id):
            return VJob(storage_path+"/"+id)
        else:
            return None

    def add_job(self, job_id):
        storage_path = csys.storage_path()
        jobs_list_file = metadata.ConfigFile(storage_path+"/jobs.json")
        job_id_list = jobs_list_file.read_variable("jobs_list", [])
        job_id_list.append(job_id)
        jobs_list_file.write_variable("jobs_list", job_id_list)

    def jobs(self, condition):
        storage_path = csys.storage_path()
        jobs_list_file = metadata.ConfigFile(storage_path+"/jobs.json")
        job_id_list = jobs_list_file.read_variable("jobs_list", [])
        job_list = []
        for job_id in job_id_list:
            job = VJob(storage_path + "/" + job_id)
            if job.job_type() == "container":
                job = VContainer(job.path)
            elif job.job_type() == "image":
                job = VImage(job.path)
            else:
                continue
            # print("{0} {1}".format(job, job.status()), file=sys.stderr)
            if job.status() == condition:
                job_list.append(job)
        return job_list
    """


    def get_current_project(self):
        """ Get the name of the current working project.
        If there isn't a working project, return None
        """
        local_config_file = metadata.ConfigFile(self.local_config_path)
        current_project = local_config_file.read_variable("current_project", None)
        if current_project is None:
            return None
        else:
            projects_path = local_config_file.read_variable("projects_path")
            path = projects_path.get(current_project, "no_place|")
            if path == "no_place|":
                projects_path[current_project] = "no_place|"
            if not os.path.exists(path):
                projects_path.pop(current_project)
                if projects_path != {}:
                    current_project = list(projects_path.keys())[0]
                else:
                    current_project = None
                local_config_file.write_variable("current_project", current_project)
                local_config_file.write_variable("projects_path", projects_path)
                return self.get_current_project()
            else:
                return current_project

    def projects(self):
        """ Get the list of all the projects.
        If there is not a list create one.
        """
        local_config_file = metadata.ConfigFile(self.local_config_path)
        projects_path = local_config_file.read_variable("projects_path", {})
        return list(projects_path.keys())

    def project_path(self):
        """ Get The path of a specific project.
        You must be sure that the project exists.
        This function don't check it.
        """
        project_name = self.get_current_project()
        local_config_file = metadata.ConfigFile(self.local_config_path)
        projects_path = local_config_file.read_variable("projects_path")
        return projects_path[project_name]



