from Chern.kernel.VProject import VProject
from Chern.kernel.VProject import new_project
from Chern.kernel.ChernDatabase import ChernDatabase
import cmd, sys, os
import Chern.interface.shell as shell
import click
from Chern.interface.ChernManager import get_manager

manager = get_manager()
current_project_name = manager.get_current_project()
from Chern.interface.ChernManager import create_object_instance as obj

if current_project_name is not None:
    current_project_path = manager.get_project_path(current_project_name)
    if os.path.exists(current_project_path) is None:
        current_project_name
if current_project_name is None:
    # FIXME may exsit
    # os.mkdir(os.environ["HOME"] +"/.Chern")
    project_name = input("please input the new project name: ")
    new_project(project_name)
    current_project_name = manager.get_current_project()

cherndb = ChernDatabase.instance()

class ChernShell(cmd.Cmd):
    intro = ''
    prompt = '[Chern]'
    file = None
    def init(self):
        current_project_name = manager.get_current_project()
        current_project_path = manager.get_project_path(current_project_name)
        manager.p = VProject(current_project_path)
        manager.c = manager.p
        os.chdir(current_project_path)


    def preloop(self):
        current_project_name = manager.get_current_project()
        self.prompt = "[Chern]["+current_project_name+"]["+os.path.relpath(manager.c.path, cherndb.project_path())+"] "

    def do_ls(self, arg):
        try:
            manager.current_object().ls()
        except Exception as e:
            print(e)

    def do_cd_project(self, arg):
        """ switch project
        """
        project = arg.split()[0]
        shell.cd_project(project)

    def do_cd(self, arg):
        """ Switch directory or object
        """
        try:
            myobject = arg.split()[0]
            shell.cd(myobject)
            current_project_name = manager.get_current_project()
            self.prompt = "[Chern]["+current_project_name+"]["+os.path.relpath(manager.c.path, cherndb.project_path())+"] "

        except Exception as e:
            print(e)

    def do_mv(self, arg):
        """ Move directory or object
        """
        source = arg.split()[0]
        destination = arg.split()[1]
        try:
            shell.mv(source, destination)
        except Exception as e:
            print(e)

    def do_cp(self, arg):
        """ Copy directory or object
        """
        source = arg.split()[0]
        destination = arg.split()[1]
        try:
            shell.cp(source, destination)
        except Exception as e:
            print(e)

    def do_rm(self, arg):
        """ Remove an object
        """
        obj = arg.split()[0]
        try:
            shell.rm(obj)
        except Exception as e:
            print(e)

    def do_ls_projects(self, arg):
        """ List all projects
        """
        try:
            manager.ls_projects()
        except Exception as e:
            print(e)

    def do_impress(self, arg):
        try:
            manager.current_object().impress()
        except Exception as e:
            print(e)

    def do_mktask(self, arg):
        try:
            obj = arg.split()[0]
            shell.mktask(obj)

        except Exception as e:
            print(e)

    def do_mkdata(self, arg):
        try:
            obj = arg.split()[0]
            shell.mkdata(obj)

        except Exception as e:
            print(e)

    def do_helpme(self, arg):
        try:
            manager.current_object().helpme(arg)
        except Exception as e:
            print(e)

    def do_submit(self, arg):
        try:
            manager.current_object().submit()
        except Exception as e:
            print(e)


    def jobs(line):
        shell.jobs

    def emptyline(self):
        pass

    def do_EOF(self, line):
        return True
        pass


