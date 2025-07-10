""" This module is used to manage the file system of the VObject
"""
import os
from os.path import join
from os.path import normpath
import shutil
from dataclasses import dataclass
from logging import getLogger

from ..utils import csys
from ..utils.message import Message
from ..utils import metadata
from .vobj_core import Core

from .chern_cache import ChernCache
from .chern_communicator import ChernCommunicator
CHERN_CACHE = ChernCache.instance()

logger = getLogger("ChernLogger")


@dataclass
class LsParameters:
    """ Light weighted data class to store the parameters of ls
    """
    readme: bool = True
    predecessors: bool = True
    sub_objects: bool = True
    status: bool = False
    successors: bool = False

class FileManagement(Core):
    """ This class is used to manage the file system of the VObject
    """
    def ls(self, show_info=LsParameters()):
        """ Print the subdirectory of the object
        I recommend to print also the README
        and the parameters|inputs|outputs ...
        """

        logger.debug("VObject ls: %s", self.invariant_path())

        message = self.printed_dite_status()

        if show_info.readme:
            message.add("README: \n", "comment")
            message.add(self.readme(), "comment")
            message.add("\n")

        sub_objects = self.sub_objects()
        if show_info.sub_objects:
            message.append(self.show_sub_objects(sub_objects, show_info))

        total = len(sub_objects)
        predecessors = self.predecessors()
        if predecessors and show_info.predecessors:
            message.append(self.show_predecessors(predecessors, total))

        total += len(predecessors)
        successors = self.successors()
        if successors and show_info.successors:
            message.append(self.show_successors(successors, total))

        return message

    def show_status(self):
        """ Show the status of the task.
        """
        status = self.status()
        status_color_map = {
            "new": "normal",
            "impressed": "success"
        }

        status_color = status_color_map.get(status, "")

        message = Message()
        message.add("**** STATUS: ", "title0")
        message.add(f"[{status}]", status_color)
        message.add("\n")
        return message

    def printed_status(self): # pylint: disable=too-many-branches
        """ Printed the status of the object"""

        message = Message()

        message.add(f"Status of : {self.invariant_path()}\n")
        if self.is_task_or_algorithm():
            if self.status() == "impressed":
                message.add("Impression: ")
                message.add(f"{'['+self.impression().uuid+']'}", 'success')
                message.add("\n")
            else:
                message.add("Impression: ")
                message.add("[new]")
                message.add("\n")
                return message
        else:
            if self.status() == "impressed":
                message.add("All the subobjects are ")
                message.add("[impressed]", 'success')
                message.add(".\n")
            else:
                message.add("Some subobjects are ")
                message.add("[not impressed]", 'normal')
                message.add(".\n")
                for sub_object in self.sub_objects():
                    message.add(sub_object.status())
                    if sub_object.status() == "new":
                        message.add(f"Subobject {sub_object} is ")
                        message.add("[not impressed]", 'normal')
                        message.add("\n")
                return message

        cherncc = ChernCommunicator.instance()
        dite_status = cherncc.dite_status()
        if dite_status == "ok":
            message.add("DITE: ")
            message.add("[connected]")
            message.add("\n")
        else:
            message.add("DITE: ")
            message.add("[unconnected]", "warning")
            message.add("\n")
            return message

        if self.is_task_or_algorithm():
            deposited = cherncc.is_deposited(self.impression())
            if deposited == "FALSE":
                message.add("Impression not deposited in DITE\n")
                return message

        if not self.is_task_or_algorithm():
            job_status = self.job_status()
            message.add(f"{'Job status':<10}: ")
            message.add(f"{'['+job_status+']'}\n")
            message.add("---------------\n")
            objects = []
            for sub_object in self.sub_objects():
                objects.append((str(sub_object), sub_object.job_status()))

            max_width = max(len(name) for name, _ in objects)

            for name, status in objects:
                message.add(f"{name:<{max_width}}: ")
                message.add(f"[{status}]")
        return message

    def printed_dite_status(self):
        """ Print the status of the DITE"""
        cherncc = ChernCommunicator.instance()
        message = Message()
        message.add(">>>> DITE: ", "title0")
        status = cherncc.dite_status()
        if status == "ok":
            message.add("[connected]", "success")
        elif status == "unconnected":
            message.add("[unconnected]", "warning")
        message.add("\n")
        return message

    def show_sub_objects(self, sub_objects, show_info):
        """ Show the sub_objects"""
        message = Message()
        sub_objects = self.sub_objects()
        sub_objects.sort(key=lambda x: (x.object_type(), x.path))
        if sub_objects:
            message.add(">>>> Subobjects:\n", "title0")

        for index, sub_object in enumerate(sub_objects):
            sub_path = self.relative_path(sub_object.path)
            if show_info.status:
                # FIXME
                status = "[FIXME]"
                color_tag = self.color_tag(status)
                message.add(f"[{index}] {f'({sub_object.object_type()})':<12} "
                            f"{sub_path:>20} ")
                message.add(f"({status})", color_tag)
                message.add("\n")
            else:
                message.add(f"[{index}] {f'({sub_object.object_type()})':<12} {sub_path:>20}\n")
        return message

    def show_predecessors(self, predecessors, total):
        """ Show the predecessors of the object"""
        message = Message()

        # Header
        message.add("o--> Predecessors:\n", "title0")

        # Sort the predecessors by alias
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        alias_list = yaml_file.read_variable("alias", [])
        predecessors.sort(
            key=lambda x: alias_list.index(self.path_to_alias(x.invariant_path()))
            if self.path_to_alias(x.invariant_path()) in alias_list
            else -1,
        )

        # Emit each predecessor
        for index, pred_object in enumerate(predecessors):
            alias = self.path_to_alias(pred_object.invariant_path())

            # --- temporary alias‑list patch (delete after new version) ---
            yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
            alias_list = yaml_file.read_variable("alias", [])
            if alias and alias not in alias_list:
                alias_list.append(alias)
            yaml_file.write_variable("alias", alias_list)
            # -------------------------------------------------------------

            order     = f"[{total + index}]"
            obj_type  = f"({pred_object.object_type()})"
            pred_path = pred_object.invariant_path()
            line = f"{order} {obj_type:<12} {alias:>10}: @/{pred_path:<20}\n"
            message.add(line)

        return message

    def show_successors(self, successors, total):
        """ Show the successors of the object"""
        message = Message()
        message.add("-->o Successors:\n", "title0")
        for index, succ_object in enumerate(successors):
            alias = self.path_to_alias(succ_object.invariant_path())
            order = f"[{total+index}]"
            succ_path = (
                succ_object.invariant_path()
            )
            obj_type = f"({succ_object.object_type()})"
            message.add(f"{order} {obj_type:<12} {alias:>10}: @/{succ_path:<20}\n")
        return message

    def copy_to_check(self, new_path): # UnitTest: DONE
        """ Check if the new path is valid for copying
        """
        # Check if the destination directory exists
        destination_dir = os.path.dirname(new_path)
        if not os.path.exists(destination_dir) and destination_dir:
            logger.warning("Warning: Destination directory '%s' does not exist.", destination_dir)
            return False

        # Check if source and destination paths are the same
        if os.path.abspath(self.path) == os.path.abspath(new_path):
            logger.warning("Warning: Source and destination paths are the same.")
            return False

        # Check if the destination path already exists
        if os.path.exists(new_path):
            logger.warning("Warning: Destination path '%s' already exists.", new_path)
            return False

        return True

    def copy_to_deal_with_arcs(self, queue, new_path): # UnitTest: DONE
        """ Deal with the arcs when copying
        """
        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = self.get_vobject(norm_path)
            new_object.clean_flow()
            new_object.clean_impressions()

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = self.get_vobject(norm_path)
            for pred_object in obj.predecessors():
                # if in the outside directory
                if self.relative_path(pred_object.path).startswith(".."):
                    pass
                else:
                    # if in the same tree
                    relative_path = self.relative_path(pred_object.path)
                    new_object.add_arc_from(self.get_vobject(
                        join(new_path, relative_path))
                    )
                    alias1 = obj.path_to_alias(pred_object.invariant_path())
                    norm_path = normpath(
                        join(new_path, relative_path)
                    )
                    new_object.set_alias(
                        alias1,
                        self.get_vobject(norm_path).invariant_path()
                    )

            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    pass

    def copy_to(self, new_path): # UnitTest: DONE
        """ Copy the current objects and its containings to a new path.
        """

        if not self.copy_to_check(new_path):
            return

        queue = self.sub_objects_recursively()
        # Make sure the related objects are all impressed
        for obj in queue:
            if not obj.is_task_or_algorithm():
                continue
            if not obj.is_impressed_fast():
                obj.impress()

        shutil.copytree(self.path, new_path)

        self.copy_to_deal_with_arcs(queue, new_path)

         # Deal with the impression
        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(f"{new_path}/{self.relative_path(obj.path)}")
            if obj.object_type() == "directory":
                continue
            new_object = self.get_vobject(norm_path)
            new_object.impress()

    def move_to_deal_with_arcs(self, queue, new_path): # UnitTest: DONE
        """ Deal with the arcs when moving
        """
        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = self.get_vobject(norm_path)
            new_object.clean_flow()

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = self.get_vobject(norm_path)
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    # if in the outside directory
                    new_object.add_arc_from(pred_object)
                    alias = obj.path_to_alias(pred_object.invariant_path())
                    new_object.set_alias(alias, pred_object.invariant_path())
                else:
                    # if in the same tree
                    relative_path = self.relative_path(pred_object.path)
                    new_object.add_arc_from(
                        self.get_vobject(join(new_path, relative_path))
                    )
                    alias1 = obj.path_to_alias(pred_object.invariant_path())
                    alias2 = pred_object.path_to_alias(obj.invariant_path())
                    norm_path = normpath(
                        join(new_path, relative_path)
                    )
                    new_object.set_alias(
                        alias1,
                        self.get_vobject(norm_path).invariant_path()
                    )
                    self.get_vobject(norm_path).set_alias(
                        alias2,
                        new_object.invariant_path()
                    )

            for succ_object in obj.successors():
                # if in the outside directory
                if self.relative_path(succ_object.path).startswith(".."):
                    new_object.add_arc_to(succ_object)
                    succ_object.remove_arc_from(self)
                    alias = succ_object.path_to_alias(obj.invariant_path())
                    succ_object.remove_alias(alias)
                    succ_object.set_alias(alias, new_object.invariant_path())

        for obj in queue:
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    obj.remove_arc_from(pred_object)

            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    obj.remove_arc_to(succ_object)


    def move_to(self, new_path): # UnitTest: DONE
        """ move to another path
        """
        if not self.move_to_check(new_path):
            return

        queue = self.sub_objects_recursively()

        # Make sure the related objects are all impressed
        all_impressed = True
        for obj in queue:
            if not obj.is_task_or_algorithm():
                continue
            if not obj.is_impressed_fast():
                all_impressed = False
                print(f"The {obj.object_type()} {obj} is not impressed,"
                      f" please impress it and try again")
        if not all_impressed:
            return

        shutil.copytree(self.path, new_path)

        self.move_to_deal_with_arcs(queue, new_path)

        shutil.rmtree(self.path)

    def move_to_check(self, new_path): # UnitTest: DONE
        """ Check if the new path is valid for moving"""
        if self.path.lower() == new_path.lower():
            print("The source and destination paths are the same.")
            return False
        return True

    def rm(self): # UnitTest: DONE
        """ Remove this object.
        The important thing is to unalias.
        """
        queue = self.sub_objects_recursively()
        for obj in queue:
            for pred_object in obj.predecessors():
                if self.relative_path(pred_object.path).startswith(".."):
                    obj.remove_arc_from(pred_object)
                    alias = pred_object.path_to_alias(pred_object.path)
                    pred_object.remove_alias(alias)

            for succ_object in obj.successors():
                if self.relative_path(succ_object.path).startswith(".."):
                    obj.remove_arc_to(succ_object)
                    alias = succ_object.path_to_alias(succ_object.path)
                    succ_object.remove_alias(alias)

        shutil.rmtree(self.path)

    def sub_objects(self): # UnitTest: DONE
        """ return a list of the sub_objects
        """
        sub_directories = os.listdir(self.path)
        sub_object_list = []
        for item in sub_directories:
            if os.path.isdir(join(self.path, item)):
                obj = self.get_vobject(join(self.path, item))
                if obj.is_zombie():
                    continue
                sub_object_list.append(obj)
        return sub_object_list

    def sub_objects_recursively(self): # UnitTest: DONE
        """ Return a list of all the sub_objects
        """
        queue = [self]
        index = 0
        while index < len(queue):
            top_object = queue[index]
            queue += top_object.sub_objects()
            index += 1
        return queue

    def import_file(self, path):
        """
        Import the file to this task directory
        """
        if not self.is_task_or_algorithm():
            print("This function is only available for task or algorithm.")
            return

        if not os.path.exists(path):
            print("File does not exist.")
            return

        filename = os.path.basename(path)
        if os.path.exists(self.path + "/" + filename):
            print("File already exists.")
            return

        if os.path.isdir(path):
            csys.copy_tree(path, self.path + "/" + filename)
        else:
            csys.copy(path, self.path + "/" + filename)

    def rm_file(self, file):
        """
        Remove the files within a task or an algorithm
        """
        if not self.is_task_or_algorithm():
            print("This function is only available for task or algorithm.")
            return

        abspath = self.path + "/" + file

        if not os.path.exists(abspath):
            print("File does not exist.")
            return

        # protect: the file should not go out of the task directory
        if self.relative_path(abspath).startswith(".."):
            print("The file should not go out of the task directory.")
            return

        # protect: the file should not be the task directory
        if self.relative_path(abspath) == ".":
            print("The file should not be the task directory.")
            return

        # protect: should not remove the .chern and chern.yaml
        if self.relative_path(abspath) in (".chern", "chern.yaml"):
            print("The file should not be the .chern or chern.yaml.")
            return

        if os.path.isdir(abspath):
            csys.rm_tree(abspath)
        else:
            os.remove(abspath)

    def move_file(self, file, dest_file):
        """
        Move the files within a task or an algorithm
        """
        if not self.is_task_or_algorithm():
            print("This function is only available for task or algorithm.")
            return

        abspath = self.path + "/" + file

        if not os.path.exists(abspath):
            print("File does not exist.")
            return

        # protect: the file should not go out of the task directory
        if self.relative_path(abspath).startswith(".."):
            print("The file should not go out of the task directory.")
            return

        # protect: the file should not be the task directory
        if self.relative_path(abspath) == ".":
            print("The file should not be the task directory.")
            return

        # protect: should not remove the .chern and chern.yaml
        if self.relative_path(abspath) in (".chern", "chern.yaml"):
            print("The file should not be the .chern or chern.yaml.")
            return

        # check if the destination directory exists
        dest = self.path + "/" + dest_file
        if not os.path.exists(os.path.dirname(dest)):
            print(f"Error: Destination directory '{os.path.dirname(dest)}' does not exist.")
            return

        csys.move(abspath, dest)
