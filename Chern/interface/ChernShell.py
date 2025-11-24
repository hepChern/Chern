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
from typing import Tuple

from ..interface import shell
from ..interface.ChernManager import get_manager
from ..kernel.vproject import VProject
from ..utils import csys
from ..utils.metadata import YamlFile


MANAGER = get_manager()
CURRENT_PROJECT_NAME = MANAGER.get_current_project()

class ChernShell(cmd.Cmd):
    """Interactive command shell for Chern project management."""

    intro = ''
    prompt = '[Chern]'
    file = None
    readline_file = None

    def __init__(self):
        """Initialize the shell and set custom completer delimiters."""
        super().__init__()

    def init(self) -> None:
        """Initialize the shell with current project context."""
        current_project_name = MANAGER.get_current_project()
        current_project_path = MANAGER.get_project_path(current_project_name)
        MANAGER.p = VProject(current_project_path)
        MANAGER.c = MANAGER.p
        os.chdir(current_project_path)
        self.readline_file = YamlFile(os.path.join(os.environ["HOME"], ".chern", "readline.yaml"))


    def preloop(self) -> None:
        """Set up the prompt before entering the command loop."""
        # Treat the dash as part of a command name for completion
        import readline
        # Get the default delimiters
        delims = readline.get_completer_delims()

        # Remove characters that appear inside your environment names
        # We remove: - (dash), : (colon), / (slash), . (dot)
        # for char in ['-']:
        for char in ['-', ':', '/', '.']:
            delims = delims.replace(char, '')
        readline.set_completer_delims(delims)

        current_project_name = MANAGER.get_current_project()
        current_path = os.path.relpath(MANAGER.c.path, csys.project_path(MANAGER.c.path))
        self.prompt = f"[Chern][{current_project_name}][{current_path}]\n>>>> "

    def cmdloop(self, intro=None):
        """Keep tab completion and catch Ctrl-C during input"""
        while True:
            try:
                # Call the original cmdloop() to preserve readline & completion
                return super().cmdloop(intro)
            except KeyboardInterrupt:
                # This catches Ctrl-C during typing (inside readline)
                print("^C")
                # restart the loop (this re-enters cmdloop, preserving state)
                intro = None
                continue

    def parseline(self, line: str) -> tuple[str, str, str]:
        """Parse a command line input."""
        # Split the line to isolate the command name
        parts = line.strip().split(maxsplit=1)
        if not parts:
            return None, None, line

        cmd = parts[0].replace('-', '_')  # Replace only in command
        rest = parts[1] if len(parts) > 1 else ""

        # Recombine for superclass parsing
        cmd, arg, line = super().parseline(f"{cmd} {rest}".strip())
        return cmd, arg, line

    # def parseline(self, line: str) -> Tuple[str, str, str]:
    #     """Parse a command line input."""
    #     # Replace ALL dashes with underscores to map to method names
    #     cmd, arg, line = super().parseline(line.replace('-', '_'))
    #     return cmd, arg, line

    def completenames(self, text, *ignored):
        """Complete command names based on user input."""
        matches = []

        # Get all method names that start with 'do_'
        for name in self.get_names():
            if name.startswith("do_"):
                # Convert do_create_task to create-task
                command_name = name[3:].replace('_', '-')
                if command_name.startswith(text):
                    matches.append(command_name)

        return matches

    def completedefault(self, text, line, begidx, endidx):
        """Default completion handler for commands that don't exist."""
        # Check if we're still typing the first word (no spaces)
        if ' ' not in line.strip():
            # Get the full command being typed so far
            full_command = line[:endidx].strip()

            # Get all matching commands
            all_matches = self.completenames(full_command)

            if all_matches:
                results = []
                for match in all_matches:
                    if match.startswith(full_command):
                        # Calculate the suffix that should be added after the current cursor position
                        # text represents what cmd thinks needs to be completed
                        # We need to find where 'text' starts within the full command
                        text_start_pos = full_command.rfind(text) if text else len(full_command)

                        if text_start_pos >= 0:
                            # Return the part of the match that comes after the text being completed
                            suffix = match[text_start_pos:]
                            if suffix:
                                results.append(suffix)
                        elif match == full_command:
                            # Exact match, add space
                            results.append(' ')
                return results

        return []

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

    def do_set_environment(self, arg: str) -> None:
        """Set environment for current object."""
        try:
            environment = arg.split()[0]
            shell.set_environment(environment)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an environment name. {e}")
        except Exception as e:
            print(f"Error setting environment: {e}")

    def do_setenv(self, arg: str) -> None:
        """Set environment for current object (alias for set-environment)."""
        try:
            environment = arg.split()[0]
            shell.set_environment(environment)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide an environment name. {e}")
        except Exception as e:
            print(f"Error setting environment: {e}")

    def complete_setenv(self, text: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete set_environment command with available environments."""
        # 1. Get the list
        environments = self.readline_file.read_variable("environments", [])

        # 2. Filter using 'text' (which contains the word currently being typed)
        # If text is empty, it returns the full list.
        matches = [env for env in environments if env.startswith(text)]

        return matches

    def do_set_memory_limit(self, arg: str) -> None:
        """Set memory limit for current object."""
        try:
            memory_limit = arg.split()[0]
            shell.set_memory_limit(memory_limit)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a memory limit. {e}")
        except Exception as e:
            print(f"Error setting memory limit: {e}")

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
            self.prompt = f"[Chern][{current_project_name}][{current_path}]\n>>>> "
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
        except Exception as e:
            print(f"Error moving object: {e}")

    def complete_mv(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete mv command with available paths."""
        current_path = MANAGER.c.path
        filepath = csys.strip_path_string(line[3:])
        return self.get_completions(current_path, filepath, line)

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

    def complete_cp(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete cp command with available paths."""
        current_path = MANAGER.c.path
        filepath = csys.strip_path_string(line[3:])
        return self.get_completions(current_path, filepath, line)

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

    def do_create_multi_tasks(self, arg: str) -> None:
        """Create multiple tasks with a base name and number of tasks."""
        try:
            objs = arg.split()
            if len(objs) < 2:
                print("Error: Please provide at least two task arguments: base_name and number_of_tasks.")
                return
            base_name = objs[0]
            begin_number_of_tasks = 0
            if len(objs) == 3:
                begin_number_of_tasks = int(objs[1])
            end_number_of_tasks = int(objs[-1])
            number_of_tasks = end_number_of_tasks - begin_number_of_tasks
            if number_of_tasks <= 0 and number_of_tasks > 10000:
                print("Error: number_of_tasks should be between 1 and 10000.")
                return
            for i in range(begin_number_of_tasks, end_number_of_tasks):
                task_name = f"{base_name}_{i}"
                shell.mktask(task_name)
                shell.add_parameter_subtask(task_name, "index", str(i))
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

    def complete_add_algorithm(self, text: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete add_algorithm command with available paths."""
        current_path = MANAGER.c.path
        # Use 'text' instead of slicing 'line'
        # 'text' is automatically extracted by cmd based on cursor position
        return self.get_completions(current_path, text, line)

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

    def complete_add_input(self, text: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete add_input command with available paths."""
        current_path = MANAGER.c.path
        # Use 'text' instead of slicing 'line'
        # 'text' is automatically extracted by cmd based on cursor position
        return self.get_completions(current_path, text, line)

    # def complete_add_input(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
    #     """Complete add_input command with available paths."""
    #     current_path = MANAGER.c.path
    #     filepath = csys.strip_path_string(line[9:])
    #     return self.get_completions(current_path, filepath, line)

    def do_add_multi_inputs(self, arg: str) -> None:
        """Create multiple tasks with a base name and number of tasks."""
        try:
            objs = arg.split()
            if len(objs) < 3:
                print("Error: Please provide at least tree task arguments: path/base_name, alias and number_of_tasks.")
                return
            base_name = objs[0]
            alias = objs[1]
            begin_number_of_tasks = 0
            if len(objs) == 4:
                begin_number_of_tasks = int(objs[2])
            end_number_of_tasks = int(objs[-1])
            number_of_tasks = end_number_of_tasks - begin_number_of_tasks
            if number_of_tasks <= 0 and number_of_tasks > 10000:
                print("Error: number_of_tasks should be between 1 and 10000.")
                return
            for i in range(begin_number_of_tasks, end_number_of_tasks):
                task_name = f"{base_name}_{i}"
                alias_index = f"{alias}_{i}"
                shell.add_input(task_name, alias_index)
        except Exception as e:
            print(f"Error creating task: {e}")

    def complete_add_multi_inputs(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete add_input command with available paths."""
        current_path = MANAGER.c.path
        filepath = csys.strip_path_string(line[16:])
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
                shell.submit()
            else:
                obj = arg.split()[0]
                shell.submit(obj)
        except Exception as e:
            print(f"Error submitting: {e}")

    def complete_submit(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete submit command with readline file"""
        runners = self.readline_file.read_variable("runners", [])
        if line.strip() == "submit":
            return runners
        matches = []
        for runner in runners:
            if runner.startswith(line.strip().split()[-1]):
                matches.append(runner)
        return matches

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

    def complete_import_file(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete import_file command with available paths."""
        filepath = csys.strip_path_string(line[12:])
        return self.get_completions_out(filepath, line)

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

    def do_view(self, arg: str) -> None:
        """View impressions."""
        try:
            if arg != "":
                shell.view(arg)
            else:
                shell.view()
        except Exception as e:
            print(f"Error viewing impressions: {e}")

    def complete_view(self, _: str, line: str, _begidx: int, _endidx: int) -> list:
        """Complete view command with [browsers] option"""
        options = ["firefox", "chrome", "safari", "edge", "browsers"]
        if line.strip() == "view":
            return options
        for option in options:
            if option.startswith(line.strip().split()[-1]):
                return [option]
        return []

    def do_danger_call(self, arg: str) -> None:
        """Dangerous call to execute a command directly."""
        try:
            cmd = arg
            shell.danger_call(cmd)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a command to execute. {e}")
        except Exception as e:
            print(f"Error executing command: {e}")

    def do_workaround(self, arg):
        """Workaround to test/debug the task."""
        try:
            status, info = shell.workaround_preshell()
            if not status:
                print(info)
                return
            # Remember the current path
            path = os.getcwd()
            # Switch to the ~
            os.chdir(info)
            # os.system(os.environ.get("SHELL", "/bin/bash"))
            # use docker if arg is docker
            if arg.strip() == "docker":
                os.system("docker run -it rootproject/root:6.36.00-ubuntu25.04 bash")
            else:
                os.system(os.environ.get("SHELL", "/bin/bash"))
            shell.workaround_postshell()
            # Switch back to the original path
            os.chdir(path)
        except (IndexError, ValueError) as e:
            print(f"Error: Please provide a command to execute. {e}")
        except Exception as e:
            print(f"Error executing command: {e}")

    def do_draw_dag(self, arg):
        """
        Generates a dependency DAG.
        ... (Docstring unchanged) ...
        """
        import os
        import plotly.graph_objects as go
        import networkx as nx
        from colorsys import hls_to_rgb, rgb_to_hls

        # --- Helper function for color manipulation --- (Unchanged)
        def lighten_color(hex_color, depth_factor):
            # Convert hex to RGB (0-255 range)
            h = hex_color.lstrip('#')
            rgb = tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

            # Convert RGB to HLS
            hls = rgb_to_hls(*rgb)

            base_lightness = hls[1]
            new_lightness = max(0.1, min(0.9, base_lightness + 0.15 * (depth_factor % 5)))

            # Convert HLS back to RGB (0-1 range)
            r, g, b = hls_to_rgb(hls[0], new_lightness, hls[2])

            # Convert RGB (0-255) back to hex
            return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

        # ------------------------------------------------------------------
        # 🎨 COLOR DEFINITIONS (Unchanged)
        # ------------------------------------------------------------------
        BASE_COLOR_MAP = {
            'red': '#FF4500',    # OrangeRed
            'blue': '#4169E1',   # RoyalBlue
            'green': '#3CB371',  # MediumSeaGreen
            'yellow': '#FFD700', # Gold
        }

        BASE_COLOR_LIST = list(BASE_COLOR_MAP.values())

        NODE_BORDER_COLOR = '#333'  # Dark Gray marker border color
        EDGE_COLOR_DEFAULT = '#D3D3D3' # Default fallback line color
        EDGE_HOVER_COLOR = 'black'  # Edge color when hovering (Trace lines are black)
        LABEL_COLOR = 'black'       # Color for permanent text labels

        top_level_map = {}
        next_base_color_index = 0
        # ------------------------------------------------------------------

        # 1 & 2. Arguments and Graph Building (Unchanged)
        args = arg.split()
        exclude_algorithms = "-x" in args
        show_permanent_labels = "-L" in args

        output_file = next((a for a in args if not a.startswith("-")), "dag.html")
        output_file = os.path.join(os.environ["HOME"], "Downloads", output_file) if output_file else None

        try:
            G = MANAGER.c.build_dependency_dag(exclude_algorithms=exclude_algorithms)
        except Exception as e:
            print(f"Error building DAG: {e}")
            return

        if not G.nodes:
            print("Graph is empty.")
            return

        print("Generating graph...")

        # 3. Layout (Positions) and Pre-calculate Colors 🎨 (Unchanged)
        print("Calculating hierarchical layout (Top-to-Bottom)...")

        node_map = {}; node_label_map = {}; NODE_COLOR_MAP = {}

        for node in G.nodes():
            # ... (Node mapping and path logic unchanged) ...
            if G.nodes[node].get('node_type') == 'aggregate':
                simple_id = G.nodes[node]['label']
                node_path = G.nodes[node].get('aggregated_path', simple_id)
            else:
                simple_id = node.invariant_path() if hasattr(node, 'invariant_path') else str(node)
                node_path = simple_id
                if callable(node_path): node_path = node_path()

            node_map[node] = simple_id
            node_label_map[simple_id] = simple_id

            # --- COLOR CALCULATION ---
            path_segments = node_path.replace("AGGREGATE:", "").strip("/").split('/')
            top_level_group = path_segments[0] if path_segments else 'default'
            depth = len(path_segments) - 1

            if top_level_group not in top_level_map:
                base_color = BASE_COLOR_LIST[next_base_color_index % len(BASE_COLOR_LIST)]
                top_level_map[top_level_group] = base_color
                next_base_color_index += 1
            else:
                base_color = top_level_map[top_level_group]

            final_color = lighten_color(base_color, depth)
            NODE_COLOR_MAP[node] = final_color
            # --- END COLOR CALCULATION ---

        H = nx.relabel_nodes(G, node_map)

        try:
            pos_simple = nx.nx_pydot.graphviz_layout(H, prog="dot")
            pos = {original_node: pos_simple[node_map[original_node]] for original_node in G.nodes()}

        except (ImportError, FileNotFoundError, Exception) as e:
            print(f"Warning: Layout error ({type(e).__name__}). Falling back to spring layout.")
            pos = nx.spring_layout(G, weight='weight', k=0.15, iterations=50)


        # 4. Create Edges (Traces) - **MODIFIED FOR HOVER SENSITIVITY**
        edge_traces = []
        arrow_annotations = []

        for u, v, data in G.edges(data=True):
            if data.get('type') != 'dependency': continue

            edge_base_color = NODE_COLOR_MAP.get(u, EDGE_COLOR_DEFAULT)

            x0, y0 = pos[u]
            x1, y1 = pos[v]

            source_label = node_label_map.get(node_map.get(u), str(u))
            target_label = node_label_map.get(node_map.get(v), str(v))
            hover_text = f"Source: {source_label}<br>Target: {target_label}"

            # 🎯 4a. GHOST HOVER TRACE: Invisible, thick line to capture hover events
            # recalculate the x0, y0, x1, y1 for better hover area
            # with a dr = 5
            dr_hover = 20
            x0_hover = x0 + (x1 - x0) * dr_hover / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            y0_hover = y0 + (y1 - y0) * dr_hover / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            x1_hover = x1 - (x1 - x0) * dr_hover / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            y1_hover = y1 - (y1 - y0) * dr_hover / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            ghost_hover_trace = go.Scatter(
                x=[x0_hover, x1_hover, None],
                y=[y0_hover, y1_hover, None],
                # line=dict(width=10, color='rgba(0,0,0,0)'), # Invisible but thick line
                line=dict(width=10, color='rgba(0,0,0,0)'), # Invisible but thick line
                hoverinfo='text',
                hovertext=hover_text,
                mode='lines',
                opacity=0, # Completely invisible
                # Use a slightly darker color for the hover label text (optional, but good contrast)
                hoverlabel=dict(bgcolor="white", font=dict(size=10, color=EDGE_HOVER_COLOR))
            )
            edge_traces.append(ghost_hover_trace)

            # 🎯 4b. VISIBLE EDGE TRACE: Thin, colored line drawn over the ghost line
            # dr_visible = 15
            # x0_visible = x0 + (x1 - x0) * dr_visible / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            # y0_visible = y0 + (y1 - y0) * dr_visible / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            # x1_visible = x1 - (x1 - x0) * dr_visible / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            # y1_visible = y1 - (y1 - y0) * dr_visible / (( (x1 - x0)**2 + (y1 - y0)**2 )**0.5)
            # x0, y0, x1, y1 = x0_visible, y0_visible, x1_visible, y1_visible
            visible_edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=2.5, color=edge_base_color),
                hoverinfo='none', # Crucially, disable hover on the visible line
                mode='lines',
                opacity=0.8,
            )
            edge_traces.append(visible_edge_trace)

            arrow_length = 50
            arrow_x0 = x1 - (arrow_length * (x1 - x0)) / (((x1 - x0)**2 + (y1 - y0)**2)**0.5)
            arrow_y0 = y1 - (arrow_length * (y1 - y0)) / (((x1 - x0)**2 + (y1 - y0)**2)**0.5)
            arrow_x1 = x1
            arrow_y1 = y1

            # 4c. Create Arrowhead annotation
            arrow_annotations.append(
                dict(
                    ax=arrow_x0, ay=arrow_y0, axref='x', ayref='y', x=arrow_x1, y=arrow_y1, xref='x', yref='y',
                    showarrow=True, arrowhead=2, arrowsize=2, arrowwidth=1,
                    arrowcolor=edge_base_color,
                    standoff=12

                )
            )


        # 5. Create Nodes (Trace) (Unchanged)
        node_x = []; node_y = []; node_text = []; node_colors = []
        permanent_annotations = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x); node_y.append(y)
            node_colors.append(NODE_COLOR_MAP[node])

            if G.nodes[node].get('node_type') == 'aggregate':
                 text_label = G.nodes[node]['label']
            else:
                 text_label = getattr(node, 'invariant_path', str(node))
                 if callable(text_label): text_label = text_label()

            node_text.append(text_label)

            permanent_annotations.append(
                dict(
                    x=x, y=y + 15,
                    xref='x', yref='y',
                    text=text_label,
                    showarrow=False,
                    font=dict(size=10, color=LABEL_COLOR),
                    xanchor='center', yanchor='bottom'
                )
            )

        # Node trace (created last to ensure it is in the foreground)
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers', hoverinfo='text',
            marker=dict(
                showscale=False,
                color=node_colors,
                size=20,
                line_width=2,
                line_color=NODE_BORDER_COLOR
            ),
        )
        node_trace.text = node_text

        # 6 & 7. Figure, Annotations, and Output (Unchanged)
        layout = go.Layout(
            title=dict(
                text=f'Dependency DAG: {MANAGER.c.invariant_path()}', font=dict(size=16)
            ),
            showlegend=False, hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )

        # TRACE ORDER: (Ghost Edges -> Visible Edges -> Nodes)
        fig = go.Figure(data=edge_traces + [node_trace], layout=layout)

        annotations = arrow_annotations

        if show_permanent_labels:
            annotations.extend(permanent_annotations)

        fig.update_layout(annotations=annotations)

        if output_file:
            if "." not in output_file: output_file += ".html"
            print(f"Saving graph to {output_file}...")

            if output_file.endswith(('.png', '.jpeg', '.jpg', '.pdf', '.svg')):
                try:
                    fig.write_image(output_file)
                    print("Done.")
                except ValueError as e:
                    print(f"Error saving image: {e}")
                    print("To save as static image, install kaleido: pip install -U kaleido")
            else:
                fig.write_html(output_file)
                print(f"Done. Open '{output_file}' in your browser to view.")


    def help_draw_dag(self):
        """Help message for draw-dag."""
        print('\n'.join([
            "draw-dag [-x]",
            "Generates and displays a dependency graph (DAG) starting from the current object.",
            "The graph shows the object's predecessors (dependencies) recursively.",
            "Options:",
            "  -x: Exclude objects whose type is 'algorithm' from the graph.",
            "",
            "Requires 'matplotlib' and optionally 'pydot' or 'pygraphviz' for best layout.",
        ]))

    def do_system_shell(self, arg):
        """Enter a system shell (bash). Type 'exit' or press Ctrl-D to return."""
        print("Entering system shell. Type 'exit' to return.\n")

        # Ensure Ctrl-C doesn’t kill the main Python process
        # old_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)

        try:
            os.system(os.environ.get("SHELL", "/bin/bash"))
        finally:
            # Restore Python's default SIGINT handling
            # signal.signal(signal.SIGINT, old_handler)
            pass

        print("\nReturned to Chern Shell.")


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
        # Calculate the full path to look in
        full_search_path = os.path.join(current_path, filepath)

        # Separate the directory user typed from the file prefix user typed
        # Example: filepath = "Task/r" -> user_dir = "Task", user_base = "r"
        user_dir = os.path.dirname(filepath)
        dirname = os.path.dirname(full_search_path)
        basename = os.path.basename(full_search_path)

        if os.path.exists(dirname):
            # Get all files in that directory
            candidates = [f for f in os.listdir(dirname) if not f.startswith('.chern')]

            # Filter for matches
            matches = [f for f in candidates if f.startswith(basename)]

            # CRITICAL FIX:
            # If the user typed a directory (user_dir), we must prepend it
            # to the results so Readline replaces "Task/r" with "Task/read"
            if user_dir:
                return [os.path.join(user_dir, m) for m in matches]

            return matches

        return []

    # def get_completions(self, current_path: str, filepath: str, line: str) -> list:
    #     """Get command completions for file paths."""
    #     path = os.path.join(current_path, filepath)
    #     if os.path.exists(path):
    #         listdir = os.listdir(path)
    #         if line.endswith("/"):
    #             return [f for f in listdir if f != ".chern"]
    #         return []

    #     basename = os.path.basename(path)
    #     dirname = os.path.dirname(path)
    #     if os.path.exists(dirname):
    #         listdir = os.listdir(dirname)
    #         completions = [f for f in listdir if f.startswith(basename) and f != ".chern"]
    #         return completions
    #     return []

    def get_completions_out(self, abspath: str, line: str) -> list:
        """Get command completions for absolute paths."""
        if os.path.exists(abspath):
            listdir = os.listdir(abspath)
            if line.endswith("/"):
                return listdir
            return []

        basename = os.path.basename(abspath)
        dirname = os.path.dirname(abspath)
        if os.path.exists(dirname):
            listdir = os.listdir(dirname)
            completions = [f for f in listdir if f.startswith(basename)]
            return completions
        return []
