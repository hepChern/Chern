""" This module is used to manage the file system of the VObject
"""
import os
from os.path import join
from os.path import normpath
import shutil
from dataclasses import dataclass
from logging import getLogger

from ..utils import csys
from ..utils.pretty import colorize
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

        self.print_dite_status()

        if show_info.readme:
            print(colorize("README:", "comment"))
            print(colorize(self.readme(), "comment"))

        sub_objects = self.sub_objects()
        if show_info.sub_objects:
            self.show_sub_objects(sub_objects, show_info)

        total = len(sub_objects)
        predecessors = self.predecessors()
        if predecessors and show_info.predecessors:
            self.show_predecessors(predecessors, total)

        total += len(predecessors)
        successors = self.successors()
        if successors and show_info.successors:
            self.show_successors(successors, total)

    def show_status(self):
        """ Show the status of the task.
        """
        status = self.status()
        status_color_map = {
            "new": "normal",
            "impressed": "success"
        }

        status_color = status_color_map.get(status, "")
        status_str = colorize(f"[{status}]", status_color)

        # if status == "impressed":
        #     run_status = self.job_status()
        #     if run_status != "unconnected":
        #         run_status_color_map = {
        #             "unsubmitted": "warning",
        #             "failed": "warning"
        #         }
        #         status_str += colorize(
        #                 f"[{run_status}]",
        #                 run_status_color_map.get(run_status, "success")
        #         )

        print(colorize("**** STATUS:", "title0"), status_str)

    def print_status(self):
        """ Print the status of the object"""

        print(f"Status of : {self.invariant_path()}")
        if self.is_task_or_algorithm():
            if self.status() == "impressed":
                print(f"Impression: {colorize('['+self.impression().uuid+']', 'success')}")
            else:
                print(f"Impression: {colorize('[new]')}")
                return
        else:
            if self.status() == "impressed":
                print(f"All the subobjects are impressed.")
            else:
                print(f"Some subobjects are not impressed.")
                for sub_object in self.sub_objects():
                    if sub_object.status() == "new":
                        print(f"Subobject {sub_object} is not impressed.")
                return

        cherncc = ChernCommunicator.instance()
        dite_status = cherncc.dite_status()
        if dite_status == "ok":
            print(f"DIET: {colorize('[connected]')}")
        else:
            print(f"DIET: {colorize('[unconnected]')}")
            return

        if self.is_task_or_algorithm():
            deposited = cherncc.is_deposited(self.impression())
            if deposited == "FALSE":
                print("Impression not deposited in DIET")
                return

        if not self.is_task_or_algorithm():
            job_status = self.job_status()
            print(f"{'Job status':<10}: {colorize('['+job_status+']')}")
            print("---------------")
            objects = []
            for sub_object in self.sub_objects():
                objects.append((str(sub_object), sub_object.job_status()))

            max_width = max(len(name) for name, _ in objects)

            for name, status in objects:
                print(f"{name:<{max_width}}: {colorize('['+status+']')}")



    def print_dite_status(self):
        """ Print the status of the DITE"""
        cherncc = ChernCommunicator.instance()
        hosts_status = colorize(">>>> DITE: ", "title0")
        status = cherncc.dite_status()
        if status == "ok":
            hosts_status += colorize("[connected] ", "success")
        elif status == "unconnected":
            hosts_status += colorize("[unconnected] ", "warning")
        print(hosts_status)

    def show_sub_objects(self, sub_objects, show_info):
        """ Show the sub_objects"""
        sub_objects = self.sub_objects()
        sub_objects.sort(key=lambda x: (x.object_type(), x.path))
        if sub_objects:
            print(colorize(">>>> Subobjects:", "title0"))

        for index, sub_object in enumerate(sub_objects):
            sub_path = self.relative_path(sub_object.path)
            if show_info.status:
                # FIXME
                status = "[FIXME]"
                color_tag = self.color_tag(status)
                print(f"{f'[{index}]'} {f'({sub_object.object_type()})':<12} "
                      f"{sub_path:>20} ({colorize(status, color_tag)})")
            else:
                print(f"[{index}] {f'({sub_object.object_type()})':<12} {sub_path:>20}")

    def show_predecessors(self, predecessors, total):
        """ Show the predecessors of the object"""
        print(colorize("o--> Predecessors:", "title0"))

        # Sort the predecessors by the alias
        yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        alias_list = yaml_file.read_variable("alias", [])
        predecessors.sort(key=lambda x: alias_list.index(self.path_to_alias(x.invariant_path()))
                          if self.path_to_alias(x.invariant_path()) in alias_list else -1)

        for index, pred_object in enumerate(predecessors):
            alias = self.path_to_alias(pred_object.invariant_path())
            # FIXME: the following should be deleted after having the new version
            yaml_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
            alias_list = yaml_file.read_variable("alias", [])
            if alias != '' and alias not in alias_list:
                alias_list.append(alias)
            yaml_file.write_variable("alias", alias_list)
            # FIXME: end here
            order = f"[{total+index}]"
            pred_path = pred_object.invariant_path()
            obj_type = "("+pred_object.object_type()+")"
            print(f"{order} {obj_type:<12} {alias:>10}: @/{pred_path:<20}")

    def show_successors(self, successors, total):
        """ Show the successors of the object"""
        print(colorize("-->o Successors:", "title0"))
        for index, succ_object in enumerate(successors):
            alias = self.path_to_alias(succ_object.invariant_path())
            order = f"[{total+index}]"
            succ_path = (
                succ_object.invariant_path()
            )
            obj_type = f"({succ_object.object_type()})"
            print(f"{order} {obj_type:<12} {alias:>10}: @/{succ_path:<20}")


    def copy_to_check(self, new_path):
        """ Check if the new path is valid for copying
        """
        # Check if the destination directory exists
        destination_dir = os.path.dirname(new_path)
        if not os.path.exists(destination_dir) and destination_dir:
            print(f"Error: Destination directory '{destination_dir}' does not exist.")
            return False

        # Check if source and destination paths are the same
        if os.path.abspath(self.path) == os.path.abspath(new_path):
            print("Error: Source and destination paths are the same.")
            return False

        # Check if the destination path already exists
        if os.path.exists(new_path):
            print(f"Error: Destination path '{new_path}' already exists.")
            return False

        return True

    def copy_to_deal_with_arcs(self, queue, new_path):
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

    def copy_to(self, new_path):
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

    def move_to_deal_with_arcs(self, queue, new_path):
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


    def move_to(self, new_path):
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

        # Deal with the impression
        # for obj in queue:
        #     # Calculate the absolute path of the new directory
        #     if obj.object_type() == "directory":
        #         continue
        #     norm_path = normpath(
        #         join(new_path, self.relative_path(obj.path))
        #     )
        #     new_object = vobj.VObject(norm_path)

        # if self.object_type() == "directory":
        #     norm_path = normpath(
        #         join(new_path, self.relative_path(obj.path))
        #     )

        shutil.rmtree(self.path)

    def move_to_check(self, new_path):
        """ Check if the new path is valid for moving"""
        if self.path.lower() == new_path.lower():
            print("The source and destination paths are the same.")
            return False
        return True

    def rm(self):
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

    def sub_objects(self):
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

    def sub_objects_recursively(self):
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
