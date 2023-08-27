from Chern.kernel.VProject import VProject
from Chern.kernel.VProject import new_project
import cmd, sys, os
from Chern.utils import csys
import Chern.interface.shell as shell
import click
from Chern.interface.ChernManager import get_manager

manager = get_manager()
current_project_name = manager.get_current_project()
# from Chern.interface.ChernManager import create_object_instance as obj
#
# if current_project_name is not None:
#     current_project_path = manager.get_project_path(current_project_name)
#     if os.path.exists(current_project_path) is None:
#         current_project_name
#
# if current_project_name is None:
#     project_name = input("please input the new project name: ")
#     new_project(project_name)
#     current_project_name = manager.get_current_project()

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
        self.prompt = "[Chern]["+current_project_name+"]["+os.path.relpath(manager.c.path, csys.project_path(manager.c.path))+"] "

    def do_ls(self, arg):
        try:
            manager.current_object().ls()
        except Exception as e:
            print(e)

    def do_status(self, arg):
        try:
            manager.current_object().print_status()
        except Exception as e:
            print(e)

    def do_collect(self, arg):
        try:
            manager.current_object().collect()
        except Exception as e:
            print(e)

    def do_display(self, arg):
        try:
            filename = arg.split()[0]
            manager.current_object().display(filename)
        except Exception as e:
            print(e)

    def do_input(self, arg):
        try:
            input_path = arg.split()[0]
            manager.current_object().input(input_path)
        except Exception as e:
            print(e)

    def do_import(self, arg):
        try:
            input_path = arg.split()[0]
            manager.current_object().importfile(input_path)
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
            self.prompt = "[Chern]["+current_project_name+"]["+os.path.relpath(manager.c.path, csys.project_path(manager.c.path))+"] "

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

    def do_mkdir(self, arg):
        try:
            obj = arg.split()[0]
            shell.mkdir(obj)

        except Exception as e:
            print(e)

    def do_mktask(self, arg):
        try:
            obj = arg.split()[0]
            shell.mktask(obj)

        except Exception as e:
            print(e)

    def do_mkalgorithm(self, arg):
        try:
            obj = arg.split()[0]
            shell.mkalgorithm(obj)

        except Exception as e:
            print(e)

    def do_addalgorithm(self, arg):
        try:
            obj = arg.split()[0]
            shell.add_algorithm(obj)

        except Exception as e:
            print(e)

    def do_addinput(self, arg):
        try:
            obj1 = arg.split()[0]
            obj2 = arg.split()[1]
            shell.add_input(obj1, obj2)

        except Exception as e:
            print(e)

    def do_addparameter(self, arg):
        try:
            obj1 = arg.split()[0]
            obj2 = arg.split()[1]
            shell.add_parameter(obj1, obj2)

        except Exception as e:
            print(e)

    def do_rmparameter(self, arg):
        try:
            obj = arg.split()[0]
            shell.rm_parameter(obj)

        except Exception as e:
            print(e)


    def do_mkdata(self, arg):
        try:
            obj = arg.split()[0]
            shell.mkdata(obj)

        except Exception as e:
            print(e)

    def do_comment(self, arg):
        try:
            manager.current_object().comment(arg)
        except Exception as e:
            print(e)

    def do_edit_readme(self, arg):
        try:
            manager.current_object().edit_readme()
        except Exception as e:
            print(e)


    def do_helpme(self, arg):
        try:
            manager.current_object().helpme(arg)
        except Exception as e:
            print(e)

    def do_submit(self, arg):
        try:
            if arg == "":
                manager.current_object().submit()
            else:
                obj = arg.split()[0]
                manager.current_object().submit(obj)
        except Exception as e:
            print(e)

    def do_impression(self, arg):
        try:
            impression = manager.current_object().impression()
            print(impression)
        except Exception as e:
            print(e)

    def do_cat(self, arg):
        try:
            manager.current_object().cat(arg)
        except Exception as e:
            print(e)

    def jobs(line):
        shell.jobs

    def do_edit_script(self, arg):
        try:
            obj = arg.split()[0]
            shell.edit_script(obj)
        except Exception as e:
            print(e)

    def emptyline(self):
        pass

    def do_EOF(self, line):
        return True
        pass


