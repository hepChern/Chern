import os
from Chern.utils import csys
from Chern.kernel.VObject import VObject
from Chern.utils import utils
from Chern.utils.utils import debug
from Chern.interface.ChernManager import get_manager
from Chern.interface.ChernManager import create_object_instance
import shutil
from Chern.kernel.VTask import create_task
from Chern.kernel.VTask import create_data
from Chern.kernel.VAlgorithm import create_algorithm
from Chern.kernel.VDirectory import create_directory
from Chern.utils.pretty import color_print
from Chern.utils.pretty import colorize
from Chern.utils import metadata
from Chern.kernel.ChernCommunicator import ChernCommunicator
import subprocess

import time

manager = get_manager()


def cd_project(line):
    manager.switch_project(line)
    os.chdir(manager.c.path)


def shell_cd_project(line):
    cd_project(line)
    print(manager.c.path)


def cd(line):
    """
    Change the directory.
    The standalone Chern.cd command is protected.
    """
    line = line.rstrip("\n")
    if line.isdigit():
        index = int(line)
        sub_objects = manager.c.sub_objects()
        successors = manager.c.successors()
        predecessors = manager.c.predecessors()
        total = len(sub_objects)
        if index < total:
            sub_objects.sort(key=lambda x:(x.object_type(), x.path))
            cd(manager.c.relative_path(sub_objects[index].path))
            return
        index -= total
        total = len(predecessors)
        if index < total:
            cd(manager.c.relative_path(predecessors[index].path))
            return
        index -= total
        total = len(successors)
        if index < total:
            cd(manager.c.relative_path(successors[index].path))
            return
        else:
            color_print("Out of index", "remind")
            return
    else:
        # cd can be used to change directory using absolute path
        line = utils.special_path_string(line)
        if line.startswith("@/") or line == "@":
            line = csys.project_path() + line.strip("@")
        else:
            line = os.path.abspath(line)

        # Check available
        if os.path.relpath(line, csys.project_path()).startswith(".."):
            print("[ERROR] Unable to navigate to a location that is not within the project.")
            return
        if not os.path.exists(line):
            print("Directory not exists")
            return
        manager.switch_current_object(line)
        os.chdir(manager.c.path)


def mv(source, destination):
    """
    Move or rename file. Will keep the link relationship.
    mv SOURCE DEST
    or
    mv SOURCE DIRECTORY
    BECAREFULL!!
    mv SOURCE1 SOURCE2 SOURCE3 ... DIRECTORY is not supported
    use loop instead
    """
    if destination.startswith("@/") or destination == "@":
        destination = os.path.normpath(csys.project_path() + destination.strip("@"))
    else:
        destination = os.path.abspath(destination)
    if os.path.exists(destination):
        destination += "/" + source
    if source.startswith("@/") or source == "@":
        source = os.path.normpath(csys.project_path() +destination.strip("@"))
    else:
        source = os.path.abspath(source)

    VObject(source).move_to(destination)


def cp(source, destination):
    """
    Move or rename file. Will keep the link relationship.
    mv SOURCE DEST
    or
    mv SOURCE DIRECTORY
    BECAREFULL!!
    mv SOURCE1 SOURCE2 SOURCE3 ... DIRECTORY is not supported
    use loop instead
    """
    # With in a task, cp is used to copy the file to the destination
    if manager.c.object_type() == "task":
        manager.c.cp(source, destination)
        return

    # With in a algorithm, cp is used to copy the file to the destination
    if manager.c.object_type() == "algorithm":
        manager.c.cp(source, destination)
        return

    if source.startswith("@/") or source == "@":
        source = os.path.normpath(csys.project_path() + source.strip("@"))
    else:
        source = os.path.abspath(source)

    if destination.startswith("@/") or destination == "@":
        destination = os.path.join(csys.project_path(), destination.strip("@"))
    else:
        destination = os.path.abspath(destination)

    # Skip if the destination is outside the project
    if os.path.relpath(destination, csys.project_path()).startswith(".."):
        print("Destination is outside the project")
        return

    # Skip the case that the souce is the same as the destination
    if source == destination:
        print("Source is the same as destination")
        return

    # Skip the case that the destination is a subdirectory of the source
    if not os.path.relpath(destination, source).startswith(".."):
        print("Destination is a subdirectory of source")
        return

    # Skip the case that the destination is already exists
    # unless the destination is a directory/project
    if os.path.exists(destination):
        if VObject(destination).is_task_or_algorithm():
            print("Destination is a task or algorithm")
            return
        if VObject(destination).is_zombie():
            print("Illegal to copy")
            return

    # If the destination is a directory that already exists
    # the real destination should be the directory/base name of the source
    if os.path.exists(destination):
        if VObject(destination).object_type() == "directory" or VObject(destination).object_type() == "project":
            destination = os.path.join(destination, os.path.basename(source))

    # Do the legal judgement again
    # Skip the case that the souce is the same as the destination
    if source == destination:
        print("Source is the same as destination")
        return

    # Skip the case that the destination is a subdirectory of the source
    if not os.path.relpath(destination, source).startswith(".."):
        print("Destination is a subdirectory of source")
        return

    # Skip the case that the destination is already exists
    # unless the destination is a directory/project
    if os.path.exists(destination):
        if VObject(destination).is_task_or_algorithm():
            print("Destination is a task or algorithm")
            return
        if VObject(destination).is_zombie():
            print("Illegal to copy")
            return

    # Skip the case that the destination is outside the project
    if os.path.relpath(destination, csys.project_path()).startswith(".."):
        print("Destination is outside the project")
        return

    VObject(source).copy_to(destination)


def ls(line):
    """
    The function ls should not be defined here
    """
    print("Running")
    manager.current_object().ls()


def short_ls(line):
    """
    The function ls should not be defined here
    """
    manager.c.short_ls()


def mkalgorithm(obj, use_template=False):
    """ Create a new algorithm """
    line = csys.refine_path(obj, manager.c.path)
    parent_path = os.path.abspath(line+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "directory" and object_type != "project":
        print("Not allowed to create algorithm here")
        return
    create_algorithm(line, use_template)


def mktask(line):
    """ Create a new task """
    line = csys.refine_path(line, manager.c.path)
    parent_path = os.path.abspath(line+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "directory" and object_type != "project":
        print("Not allowed to create task here")
        return
    create_task(line)


def mkdata(line):
    """ Create a new data task """
    line = csys.refine_path(line, manager.c.path)
    parent_path = os.path.abspath(line+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "directory" and object_type != "project":
        print("Not allowed to create task here")
        return
    create_data(line)


def mkdir(line):
    """ Create a new directory """
    line = csys.refine_path(line, manager.c.path)
    parent_path = os.path.abspath(line+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "directory" and object_type != "project":
        print("Not allowed to create directory here")
        return
    create_directory(line)


def rm(line):
    line = os.path.abspath(line)
    # Deal with the illegal operation
    if line == csys.project_path():
        print("Unable to remove project")
        return
    if os.path.relpath(line, csys.project_path()).startswith(".."):
        print("Unable to remove directory outside the project")
        return
    if not os.path.exists(line):
        print("File not exists")
        return
    VObject(line).rm()


def add_source(line):
    # line = os.path.abspath(line)
    manager.c.add_source(line)


def jobs(line):
    object_type = manager.c.object_type()
    if object_type != "algorithm" and object_type != "task":
        print("Not able to found job")
        return
    manager.c.jobs()


def status():
    consult_id = time.time()
    if manager.c.object_type() == "task" or manager.c.object_type() == "algorithm":
        if manager.c.object_type() == "task":
            status = manager.c.status(consult_id)
        else:
            status = manager.c.status(consult_id)
        if status == "built" or status == "done":
            color_tag = "success"
        elif status == "failed":
            color_tag = "warning"
        elif status == "running":
            color_tag = "running"
        else:
            color_tag = "normal"
        color_print(status, color_tag)

    sub_objects = manager.c.sub_objects()
    sub_objects.sort(key=lambda x:(x.object_type(),x.path))
    for obj in sub_objects:
        status = create_object_instance(obj.path).status(consult_id)
        if status == "built" or status == "done" or status == "finished":
            color_tag = "success"
        elif status == "failed" or status == "unfinished":
            color_tag = "warning"
        elif status == "running":
            color_tag = "running"
        else:
            color_tag = "normal"

        print("{1:<20} {0:<20} ".format(colorize(status, color_tag), manager.c.relative_path(obj.path)) )

def importfile(filename):
    if manager.c.object_type() != "task" and manager.c.object_type() != "algorithm":
        print("Unable to call importfile if you are not in a task or algorithm.")
        return
    manager.c.importfile(filename)


def add_input(path, alias):
    if manager.c.object_type() != "task" and manager.c.object_type() != "algorithm":
        print("Unable to call add_input if you are not in a task or algorithm.")
        return
    manager.c.add_input(path, alias)


def add_algorithm(path):
    if manager.c.object_type() != "task":
        print("Unable to call add_algorithm if you are not in a task.")
        return
    manager.c.add_algorithm(path)


def add_parameter(par, value):
    if manager.c.object_type() != "task":
        print("Unable to call add_input if you are not in a task.")
        return
    manager.c.add_parameter(par, value)


def rm_parameter(par):
    if manager.c.object_type() != "task":
        print("Unable to call add_input if you are not in a task.")
        return
    manager.c.remove_parameter(par)


def remove_input(alias):
    if manager.c.object_type() != "task":
        print("Unable to call remove_input if you are not in a task.")
        return
    manager.c.remove_input(alias)


def add_host(host, url):
    cherncc = ChernCommunicator.instance()
    cherncc.add_host(host, url)


def hosts():
    cherncc = ChernCommunicator.instance()
    hosts = cherncc.hosts()
    urls = cherncc.urls()
    print("{0:<20}{1:20}".format("HOSTS", "STATUS"))
    for host in hosts:
        status = cherncc.host_status(host)
        color_tag = {"ok":"ok", "unconnected":"warning"}[status]
        print("{0:<20}{1:20}".format(host, colorize(status, color_tag)))

def dite():
    cherncc = ChernCommunicator.instance()
    dite_info = cherncc.dite_info()
    print(dite_info)

def runners():
    cherncc = ChernCommunicator.instance()
    status = cherncc.dite_status()
    if status == "unconnected":
        print(colorize("DITE unconnected, please connect first", "warning"))
        return
    runners = cherncc.runners()
    print("Number of runners registered at DITE: ", len(runners))
    if runners:
        urls = cherncc.runners_url()
        for runner, url in zip(runners, urls):
            print("{0:<20}{1:20}".format(runner, url))

def register_runner(runner, url, secret):
    cherncc = ChernCommunicator.instance()
    cherncc.register_runner(runner, url, secret)

def remove_runner(runner):
    cherncc = ChernCommunicator.instance()
    cherncc.remove_runner(runner)


def edit_script(obj):
    path = os.path.join(os.environ["HOME"], ".chern", "config.yaml")
    yaml_file = metadata.YamlFile(path)
    editor = yaml_file.read_variable("editor", "vi")
    subprocess.call([editor, manager.c.path + "/" + obj])
