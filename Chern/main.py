"""
    main function
    The purpose is to start: Chern4

    Functions:
        cli:
            default entrance, to start chern command line
        ipython: [deprecated]
            start the ipython shell of chern
        * start_chern_ipython:
            function for cli:ipython
        * start_chern_command_line:
            function for default cli

        machine:
            start or stop the chernmachine

        config:
            set the configurations: inavailable yet
        prologue:
            print the prologue
"""
import click
import os
from os.path import join
from Chern.kernel import VProject
from Chern.utils import csys
from Chern.utils import metadata
from Chern.interface.ChernShell import ChernShell
from logging import getLogger
import logging

def is_first_time():
    """ Check if it is the first time to use the software """
    return not os.path.exists(csys.local_config_dir())


def start_first_time():
    """ Start the first time """
    print("Starting the first time")
    print("Creating the config directory $HOME/.Chern")
    csys.mkdir(csys.local_config_dir())


def start_chern_command_line():
    logger = getLogger("ChernLogger")
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)

    logger.debug("def start_chern_command_line")
    print("Welcome to the CHERN Shell environment")
    print("Please type: 'helpme' to get more information")
    chern_shell = ChernShell()
    chern_shell.init()
    chern_shell.cmdloop()
    logger.debug("end start_chern_command_line")


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """ Chern command only is equal to `Chern ipython`
    """
    if is_first_time():
        start_first_time()
    if ctx.invoked_subcommand is None:
        try:
            config_file = metadata.ConfigFile(
                csys.local_config_dir() + "/config.json"
            )
            current_project = config_file.read_variable("current_project", "")
            print("Current project: ", current_project)
            if (
                current_project is None or current_project == "" or
                current_project not in config_file.read_variable(
                    "projects_path"
                ).keys()
            ):

                print("No project is selected as the current project")
                print("Please use ``chern workon PROJECT''' to select a project")
                print("Please use ``chern projects'' to list all the projects")
            else:
                start_chern_command_line()
        except Exception as e:
            print(e)
            print("Chern shell ended")


@cli.command()
def config():
    """ Configure the software"""
    print("Configuration is not supported yet")


@cli.command()
def chern_command_line():
    """ Start Chern command line with cmd """
    try:
        start_chern_command_line()
    except Exception as e:
        print("Fail to start Chern command line:", e)


@cli.command()
def init():
    """ Add the current directory to project """
    try:
        VProject.init_project()
        start_chern_command_line()
    except Exception as e:
        print(e)
        print("Chern Shell Ended")


@cli.command()
@click.argument("path", type=str)
def use(path):
    """ Use a directory as the project"""
    try:
        VProject.use_project(path)
        start_chern_command_line()
    except Exception as e:
        print("Fail to start ipython:", e)


@cli.command()
def projects():
    """ List all the projects """
    try:
        config_file = metadata.ConfigFile(csys.local_config_dir()+"/config.json")
        projects = config_file.read_variable("projects_path")
        current_project = config_file.read_variable("current_project")
        for project in projects.keys():
            if project == current_project:
                print("*", project, ":", projects[project])
            else:
                print(project, ":", projects[project])
    except Exception as e:
        print("Fail to list all the projects:", e)


@cli.command()
@click.argument("project", type=str)
def workon(project):
    """ Switch to the project ``PROJECT' """
    try:
        config_file = metadata.ConfigFile(
            join(csys.local_config_dir(), "config.json")
        )
        projects = config_file.read_variable("projects_path")
        if project in projects.keys():
            config_file.write_variable("current_project", project)
            print("Switch to project: ", project)
        else:
            print("Project ``{}'' not found".format(project))
    except Exception as e:
        print("Fail to switch to the project:", e)


@cli.command()
@click.argument("project", type=str)
def remove(project):
    """ Remove the project ``PROJECT' """
    try:
        config_file = metadata.ConfigFile(
            join(csys.local_config_dir, "config.json")
        )
        projects = config_file.read_variable("projects_path")
        current_project = config_file.read_variable("current_project")
        if project == current_project:
            config_file.write_variable("current_project", "")

        if project in projects:
            projects.pop(project)
            config_file.write_variable("projects_path", projects)
            print("Remove project: ", project)
        else:
            print("Project ``{}'' not found".format(project))
    except Exception as e:
        print("Fail to remove the project")


@cli.command()
def prologue():
    """ A prologue from the author """
    print("""
    Chern: A data analysis management toolkit
    Author: Mingrui Zhao
            2013 - 2017
          @ Center of High Energy Physics, Tsinghua University
            2017 - 2022
          @ Department of Nuclear Physics, China Institute of Atomic Energy
            2023 - 2024
          @ China Institute of Atomic Energy & Niels Bohr Institute
    Email: mingrui.zhao@mail.labz0.org

    I started the project when I was a undergraduate student
          in Tsinghua University and working for LHCb collaboration.
    And the software in LHCb is usually named after the Great name,
          such as ``Gauss'' and ``Davinci''.
    The term ``Chern''(陈) is a common surname in China
           and it is usually written as ``Chen'' in English now.
    The unusual spelling "Chern" is a transliteration
          in the old Gwoyeu Romatzyh (GR) romanization
          used in the early twentieth century China.
    Nowadays, when written in the form of ``Chern'',
          it usually refer to ``Shiing-Shen Chern'',
    the great Chinese-American mathematician who made
          fundamental contributions to differential geometry and topology.
    The well-known ``Chern classes'', ``Chern–Gauss–Bonnet theorem''
          and many others are named after him.
    This is the origin of the software name.
    """)


@click.group()
def cli_sh():
    """ Chern command line command
    """


@cli_sh.command()
def ls():
    from Chern.interface import shell
    shell.ls("")


@cli_sh.command()
@click.argument("path", type=str)
def mkdir(path):
    from Chern.interface import shell
    shell.mkdir(path)


@cli_sh.command()
def ls_projects():
    from Chern.interface import shell
    shell.ls_projects("")


@cli_sh.command()
@click.argument("project", type=str)
def cd_project(project):
    """ Switch to the project ``PROJECT'
    '"""
    from Chern.interface import shell
    shell.cd_project(project)


def sh():
    cli_sh()


def main():
    cli()
