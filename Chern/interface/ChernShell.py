"""
Chern Shell Interface Module.

This module provides an interactive command-line shell interface for managing
Chern projects, tasks, algorithms, and directories.

Note: Broad exception handling is used throughout this module to ensure
the shell remains stable and provides user-friendly error messages.
This is a common pattern in interactive shells to prevent crashes.
"""
# pylint: disable=broad-exception-caught
import cmd
import os

from ..interface import shell
from ..interface.ChernManager import get_manager
from ..kernel.vproject import VProject
from ..utils import csys

MANAGER = get_manager()
CURRENT_PROJECT_NAME = MANAGER.get_current_project()

class ChernShell(cmd.Cmd):
    """Interactive command shell for Chern project management."""

    intro = ''
    prompt = '[Chern]'
    file = None

    def init(self) -> None:
        """Initialize the shell with current project context."""
        current_project_name = MANAGER.get_current_project()
        current_project_path = MANAGER.get_project_path(current_project_name)
        MANAGER.p = VProject(current_project_path)
        MANAGER.c = MANAGER.p
        os.chdir(current_project_path)

    def preloop(self) -> None:
        """Set up the prompt before entering the command loop."""
        current_project_name = MANAGER.get_current_project()
        current_path = os.path.relpath(MANAGER.c.path, csys.project_path(MANAGER.c.path))
        self.prompt = f"[Chern][{current_project_name}][{current_path}] "

    def do_ls(self, _: str) -> None:
        """List contents of current object."""
        try:
            message = MANAGER.current_object().ls()
            print(message.colored())
        except Exception as e:
            print(f"Error listing contents: {e}")

    def do_status(self, _: str) -> None:
        """Show status of current object."""
        try:
            shell.status()
        except Exception as e:
            print(f"Error showing status: {e}")

    def do_collect(self, _: str) -> None:
        """Collect data for current object."""
        try:
            MANAGER.current_object().collect()
        except Exception as e:
            print(f"Error collecting data: {e}")

    def do_display(self, arg: str) -> None:
        """Display a file from current object."""
        try:
            filename = arg.split()[0]
            MANAGER.current_object().display(filename)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a filename. {e}")
        except Exception as e:
            print(f"Error displaying file: {e}")

    def do_input(self, arg: str) -> None:
        """Add input to current object."""
        try:
            input_path = arg.split()[0]
            MANAGER.current_object().input(input_path)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an input path. {e}")
        except Exception as e:
            print(f"Error adding input: {e}")

    def do_import(self, arg: str) -> None:
        """Import a file into current object."""
        try:
            obj = arg.split()[0]
            shell.import_file(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a file to import. {e}")
        except Exception as e:
            print(f"Error importing file: {e}")

    def do_kill(self, _: str) -> None:
        """Kill current object process."""
        try:
            MANAGER.current_object().kill()
        except Exception as e:
            print(f"Error killing process: {e}")

    def do_auto_download(self, arg: str) -> None:
        """Enable or disable auto download."""
        try:
            auto_download = arg.split()[0]
            if auto_download == "on":
                MANAGER.current_object().set_auto_download(True)
            elif auto_download == "off":
                MANAGER.current_object().set_auto_download(False)
            else:
                print("please input on or off")
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide 'on' or 'off'. {e}")
        except Exception as e:
            print(f"Error setting auto download: {e}")

    def do_cd_project(self, arg: str) -> None:
        """Switch project."""
        try:
            project = arg.split()[0]
            shell.cd_project(project)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a project name. {e}")

    def do_cd(self, arg: str) -> None:
        """Switch directory or object."""
        try:
            myobject = arg.split()[0]
            shell.cd(myobject)
            current_project_name = MANAGER.get_current_project()
            current_path = os.path.relpath(MANAGER.c.path, csys.project_path(MANAGER.c.path))
            self.prompt = f"[Chern][{current_project_name}][{current_path}] "
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a directory or object name. {e}")
        except Exception as e:
            print(f"Error changing directory: {e}")

    def complete_cd(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete cd command with available paths."""
        current_path = MANAGER.c.path
        filepath = csys.strip_path_string(line[3:])
        return self.get_completions(current_path, filepath, line)

    def do_mv(self, arg: str) -> None:
        """Move directory or object."""
        try:
            args = arg.split()
            source = args[0]
            destination = args[1]
            shell.mv(source, destination)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide source and destination. {e}")
        except Exception as e:
            print(f"Error moving object: {e}")

    def do_cp(self, arg: str) -> None:
        """Copy directory or object."""
        try:
            args = arg.split()
            source = args[0]
            destination = args[1]
            shell.cp(source, destination)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide source and destination. {e}")
        except Exception as e:
            print(f"Error copying object: {e}")

    def do_rm(self, arg: str) -> None:
        """Remove an object."""
        try:
            obj = arg.split()[0]
            shell.rm(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an object to remove. {e}")
        except Exception as e:
            print(f"Error removing object: {e}")

    def do_ls_projects(self, _: str) -> None:
        """List all projects."""
        try:
            MANAGER.ls_projects()
        except Exception as e:
            print(f"Error listing projects: {e}")

    def do_impress(self, _: str) -> None:
        """Create impression of current object."""
        try:
            MANAGER.current_object().impress()
        except Exception as e:
            print(e)

    def do_mkdir(self, arg: str) -> None:
        """Create a new directory."""
        try:
            obj = arg.split()[0]
            shell.mkdir(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a directory name. {e}")
        except Exception as e:
            print(f"Error creating directory: {e}")

    def do_create_task(self, arg: str) -> None:
        """Create a new task."""
        try:
            obj = arg.split()[0]
            shell.mktask(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a task name. {e}")
        except Exception as e:
            print(f"Error creating task: {e}")

    def do_create_algorithm(self, arg: str) -> None:
        """Create a new algorithm."""
        try:
            obj = arg.split()[0]
            shell.mkalgorithm(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an algorithm name. {e}")
        except Exception as e:
            print(f"Error creating algorithm: {e}")

    def do_add_algorithm(self, arg: str) -> None:
        """Add an algorithm to current task."""
        try:
            obj = arg.split()[0]
            shell.add_algorithm(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an algorithm path. {e}")
        except Exception as e:
            print(f"Error adding algorithm: {e}")

    def complete_add_algorithm(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete add_algorithm command with available paths."""
        current_path = MANAGER.c.path
        filepath = csys.strip_path_string(line[14:])
        return self.get_completions(current_path, filepath, line)

    def do_add_input(self, arg: str) -> None:
        """Add input with path and alias."""
        try:
            args = arg.split()
            obj1 = args[0]
            obj2 = args[1]
            shell.add_input(obj1, obj2)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide path and alias. {e}")
        except Exception as e:
            print(f"Error adding input: {e}")

    def complete_add_input(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete add_input command with available paths."""
        current_path = MANAGER.c.path
        filepath = csys.strip_path_string(line[9:])
        return self.get_completions(current_path, filepath, line)

    def do_remove_input(self, arg: str) -> None:
        """Remove an input from current object."""
        try:
            obj = arg.split()[0]
            shell.remove_input(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an input alias to remove. {e}")
        except Exception as e:
            print(f"Error removing input: {e}")

    def complete_remove_input(self, text: str, _line: str, _begidx: int, _endidx: int) -> list:
        """Complete remove_input command with available aliases."""
        if not MANAGER.c.is_task_or_algorithm():
            return []
        alias = MANAGER.c.get_alias_list()
        if text == "":
            return list(alias)
        return [f for f in alias if f.startswith(text)]

    def do_add_parameter(self, arg: str) -> None:
        """Add a parameter to current task."""
        try:
            args = arg.split()
            obj1 = args[0]
            obj2 = args[1]
            shell.add_parameter(obj1, obj2)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide parameter name and value. {e}")
        except Exception as e:
            print(f"Error adding parameter: {e}")

    def do_remove_parameter(self, arg: str) -> None:
        """Remove a parameter from current task."""
        try:
            obj = arg.split()[0]
            shell.rm_parameter(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a parameter name to remove. {e}")
        except Exception as e:
            print(f"Error removing parameter: {e}")

    def do_create_data(self, arg: str) -> None:
        """Create a new data object."""
        try:
            obj = arg.split()[0]
            shell.mkdata(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a data name. {e}")
        except Exception as e:
            print(f"Error creating data: {e}")

    def do_comment(self, arg: str) -> None:
        """Add a comment to current object."""
        try:
            MANAGER.current_object().comment(arg)
        except Exception as e:
            print(f"Error adding comment: {e}")

    def do_edit_readme(self, _: str) -> None:
        """Edit README for current object."""
        try:
            MANAGER.current_object().edit_readme()
        except Exception as e:
            print(f"Error editing README: {e}")

    def do_helpme(self, arg: str) -> None:
        """Get help for current object."""
        try:
            print(MANAGER.current_object().helpme(arg).colored())
        except Exception as e:
            print(f"Error getting help: {e}")

    def do_submit(self, arg: str) -> None:
        """Submit current object."""
        try:
            if arg == "":
                MANAGER.current_object().submit()
            else:
                obj = arg.split()[0]
                MANAGER.current_object().submit(obj)
        except Exception as e:
            print(f"Error submitting: {e}")

    def do_impression(self, _: str) -> None:
        """Get impression of current object."""
        try:
            impression = MANAGER.current_object().impression()
            print(impression)
        except Exception as e:
            print(f"Error getting impression: {e}")

    def do_cat(self, arg: str) -> None:
        """Display file contents."""
        try:
            MANAGER.current_object().cat(arg)
        except Exception as e:
            print(f"Error displaying file: {e}")

    def do_import_file(self, arg: str) -> None:
        """Import a file into current object."""
        try:
            obj = arg.split()[0]
            shell.import_file(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a file to import. {e}")
        except Exception as e:
            print(f"Error importing file: {e}")

    def do_rm_file(self, arg: str) -> None:
        """Remove files from current object."""
        try:
            objs = arg.split()
            for obj in objs:
                shell.rm_file(obj)
        except Exception as e:
            print(f"Error removing files: {e}")

    def do_mv_file(self, arg: str) -> None:
        """Move a file within current object."""
        try:
            args = arg.split()
            file1 = args[0]
            file2 = args[1]
            shell.mv_file(file1, file2)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide source and destination files. {e}")
        except Exception as e:
            print(f"Error moving file: {e}")

    def do_edit_script(self, arg: str) -> None:
        """Edit a script file."""
        try:
            obj = arg.split()[0]
            shell.edit_script(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a script name. {e}")
        except Exception as e:
            print(f"Error editing script: {e}")

    def do_config(self, _: str) -> None:
        """Edit configuration."""
        try:
            shell.config()
        except Exception as e:
            print(f"Error accessing config: {e}")

    def do_clean_impressions(self, _: str) -> None:
        """Clean impressions (developer only)."""
        try:
            print("Very dangerous operation only for developer")
            print("cleaning impression")
            MANAGER.current_object().clean_impressions()
        except Exception as e:
            print(f"Error cleaning impressions: {e}")

    def do_runners(self, _: str) -> None:
        """Show available runners."""
        try:
            shell.runners()
        except Exception as e:
            print(f"Error showing runners: {e}")

    def do_dite(self, _: str) -> None:
        """Show DITE information."""
        try:
            shell.dite()
        except Exception as e:
            print(f"Error accessing DITE: {e}")

    def do_export(self, arg: str) -> None:
        """Export file to output path."""
        try:
            args = arg.split()
            filename = args[0]
            output_path = args[1]
            MANAGER.current_object().export(filename, output_path)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide filename and output path. {e}")
        except Exception as e:
            print(f"Error exporting: {e}")

    def do_register_runner(self, arg: str) -> None:
        """Register a new runner."""
        try:
            args = arg.split()
            runner = args[0]
            url = args[1]
            secret = args[2]
            shell.register_runner(runner, url, secret)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide runner name, URL, and secret. {e}")
        except Exception as e:
            print(f"Error registering runner: {e}")

    def do_remove_runner(self, arg: str) -> None:
        """Remove a runner."""
        try:
            obj = arg.split()[0]
            shell.remove_runner(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a runner name. {e}")
        except Exception as e:
            print(f"Error removing runner: {e}")

    def do_send(self, arg: str) -> None:
        """Send a file or path."""
        try:
            obj = arg.split()[0]
            shell.send(obj)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a path to send. {e}")
        except Exception as e:
            print(f"Error sending: {e}")

    def do_impview(self, _: str) -> None:
        """View impressions."""
        try:
            shell.impview()
        except Exception as e:
            print(f"Error viewing impressions: {e}")

    def emptyline(self) -> None:
        """Handle empty line input."""

    def do_EOF(self, _: str) -> bool:  # pylint: disable=invalid-name
        """Handle EOF (Ctrl+D) to exit shell."""
        print("")
        print("Thank you for using CHERN")
        print("Contact Mingrui Zhao (mingrui.zhao@mail.labz0.org) for any questions")
        return True

    def get_completions(self, current_path: str, filepath: str, line: str) -> list:
        """Get command completions for file paths."""
        path = os.path.join(current_path, filepath)
        if os.path.exists(path):
            listdir = os.listdir(path)
            if line.endswith("/"):
                return [f for f in listdir if f != ".chern"]
            return []

        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        if os.path.exists(dirname):
            listdir = os.listdir(dirname)
            completions = [f for f in listdir if f.startswith(basename) and f != ".chern"]
            return completions
        return []
