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
from Chern.kernel import VProject
from Chern.utils import csys
from Chern.kernel.ChernDatabase import ChernDatabase
from Chern.interface.ChernShell import ChernShell
from logging import getLogger
import logging

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """ Chern command only is equal to `Chern ipython`
    """
    if is_first_time():
        start_first_time()
    if ctx.invoked_subcommand is None:
        try:
            start_chern_command_line()
        except Exception as e:
            print(e)
            print("Chern shell ended")

@cli.command()
def config():
    """ Configue the software"""
    print("Configuration is not supported yet")

@cli.command()
def ipython():
    """ Start IPython """
    try:
        start_chern_ipython()
    except:
        print("Fail to start ipython")

@cli.command()
def chern_command_line():
    """ Start Chern command line with cmd """
    try:
        start_chern_command_line()
        print("End here")
    except:
        print("Fail to start Chern command line")

@cli.command()
def init():
    """ Add the current directory to project """
    try:
        print("Init")
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
    except:
        print("Fail to start ipython")

@cli.command()
@click.argument("command", type=str)

def start_chern_ipython():
    profile_path = os.path.abspath(csys.local_config_dir()+"/profile")
    from IPython import start_ipython, get_ipython
    start_ipython(argv=["--profile=chern", "--ipython-dir="+profile_path])
    ip = get_ipython()
    del ip.magics_manager.magics["line"]["ls"]
    del ip.magics_manager.magics["line"]["ll"]
    del ip.magics_manager.magics["line"]["mv"]
    del ip.magics_manager.magics["line"]["rm"]
    del ip.magics_manager.magics["line"]["cp"]
    del ip.magics_manager.magics["line"]["mkdir"]

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


def is_first_time():
    if not os.path.exists(csys.local_config_dir()):
        return True
    if not os.path.exists(csys.local_config_dir()+"/profile"):
        return True
    cherndb = ChernDatabase.instance()
    if cherndb.projects() == []:
        return True
    return False

def start_first_time():
    csys.mkdir(csys.local_config_dir())
    data_path = os.path.abspath(os.path.dirname(__file__) + "/data/profile")
    csys.copy_tree(data_path, csys.local_config_dir()+"/profile")

def main():
    cli()

@cli.command()
def prologue():
    """ A prologue from the author """
    print("""
Chern: A data analysis management toolkit
Author: Mingrui Zhao
        2013 - 2017       @ Center of High Energy Physics, Tsinghua University
        2017 - 2022       @ Department of Nuclear Physics, China Institute of Atomic Energy
        2023 - 2023(now)  @ China Institute of Atomic Energy & Niels Bohr Institute
Email: mingrui.zhao@mail.labz0.org

I started the project when I was a undergraduate student in Tsinghua University and working for LHCb collaboration.
And the software in LHCb is usually named after the Great name, such as ``Gauss'' and ``Davinci''.
The term ``Chern''(陈) is a common surname in China and it is usually written as ``Chen'' in English now.
The unusual spelling "Chern" is a transliteration in the old Gwoyeu Romatzyh (GR) romanization used in the early twentieth century China.
Nowadays, when written in the form of ``Chern'', it usually refer to ``Shiing-Shen Chern'',
the great Chinese-American mathematician who made fundamental contributions to differential geometry and topology.
The well-known ``Chern classes'', ``Chern–Gauss–Bonnet theorem'' and many others are named after him.
This is the origin of the software name.
""")
# At the same time, my girlfriend has the same surname in Chinese with S.S.Chern.
# she is my ex now.

# I think the following things are deprecated
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
