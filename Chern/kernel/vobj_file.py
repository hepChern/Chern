""" This module is used to manage the file system of the VObject
"""
import os
from os.path import join
from os.path import normpath
import shutil
from dataclasses import dataclass
from logging import getLogger

from ..utils.pretty import colorize
from . import VObject as vobj
from .vobj_core import Core

from .chern_cache import ChernCache
from .ChernCommunicator import ChernCommunicator
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
        for index, pred_object in enumerate(predecessors):
            alias = self.path_to_alias(pred_object.invariant_path())
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
            new_object = vobj.VObject(norm_path)
            new_object.clean_flow()
            new_object.clean_impressions()

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = vobj.VObject(norm_path)
            for pred_object in obj.predecessors():
                # if in the outside directory
                if self.relative_path(pred_object.path).startswith(".."):
                    pass
                else:
                    # if in the same tree
                    relative_path = self.relative_path(pred_object.path)
                    new_object.add_arc_from(vobj.VObject(
                        join(new_path, relative_path))
                    )
                    alias1 = obj.path_to_alias(pred_object.invariant_path())
                    norm_path = normpath(
                        join(new_path, relative_path)
                    )
                    new_object.set_alias(
                        alias1,
                        vobj.VObject(norm_path).invariant_path()
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
            new_object = vobj.VObject(norm_path)
            new_object.impress()

    def move_to_deal_with_arcs(self, queue, new_path):
        """ Deal with the arcs when moving
        """
        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = vobj.VObject(norm_path)
            new_object.clean_flow()

        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = vobj.VObject(norm_path)
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
                        vobj.VObject(join(new_path, relative_path))
                    )
                    alias1 = obj.path_to_alias(pred_object.invariant_path())
                    alias2 = pred_object.path_to_alias(obj.invariant_path())
                    norm_path = normpath(
                        join(new_path, relative_path)
                    )
                    new_object.set_alias(
                        alias1,
                        vobj.VObject(norm_path).invariant_path()
                    )
                    vobj.VObject(norm_path).set_alias(
                        alias2,
                        new_object.invariant_path()
                    )

            for succ_object in obj.successors():
                # if in the outside directory
                if self.relative_path(succ_object.path).startswith(".."):
                    new_object.add_arc_to(succ_object)
                    succ_object.remove_arc_from(self)
                    alias = obj.path_to_alias(succ_object.invariant_path())
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

    def rm(self):
        """
        Remove this object.
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
                obj = vobj.VObject(join(self.path, item))
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
