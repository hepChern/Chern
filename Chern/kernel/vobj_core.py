from os.path import join
from os.path import normpath
import shutil

import Chern
from Chern.utils.pretty import colorize
from Chern.kernel.ChernCache import ChernCache
from Chern.kernel.ChernCommunicator import ChernCommunicator
import Chern.kernel.VObject as vobj

from logging import getLogger
cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")


class Core:
    def ls(self,
           show_readme=True, show_predecessors=True, show_sub_objects=True,
           show_status=False, show_successors=False):
        """ Print the subdirectory of the object
        I recommend to print also the README
        and the parameters|inputs|outputs ...
        """

        """
        FIXME: Should communicate with ChernCommunicator
        to get the runner status
        if not cherncache.is_docker_started():
            color_print("!!Warning: docker not started", color="warning")
        if daemon_status() != "started":
            color_print("!!Warning: runner not started, the status is {}"
            .format(daemon_status()), color="warning")
        """

        logger.debug("VObject ls: {}".format(self.invariant_path()))
        cherncc = ChernCommunicator.instance()

        # Should have a flag whether to show the runner
        """
        hosts = cherncc.hosts()
        hosts_status = colorize(">>>> Runners connection : ", "title0")
        for host in hosts:
            status = cherncc.host_status(host)
            if (status == "ok"):
                hosts_status += colorize("["+host+"] ", "success")
            elif (status == "unconnected"):
                hosts_status += colorize("["+host+"] ", "warning")
        print(hosts_status)
        """
        hosts_status = colorize(">>>> DITE: ", "title0")
        status = cherncc.host_status()
        if (status == "ok"):
            hosts_status += colorize("[connected] ", "success")
        elif (status == "unconnected"):
            hosts_status += colorize("[unconnected] ", "warning")
        print(hosts_status)

        if show_readme:
            print(colorize("README:", "comment"))
            print(colorize(self.readme(), "comment"))

        sub_objects = self.sub_objects()
        sub_objects.sort(key=lambda x: (x.object_type(), x.path))
        if sub_objects and show_sub_objects:
            print(colorize(">>>> Subobjects:", "title0"))

        if show_sub_objects:
            for index, sub_object in enumerate(sub_objects):
                sub_path = self.relative_path(sub_object.path)
                if show_status:
                    status = (
                        Chern.interface.ChernManager.create_object_instance(
                            sub_object.path
                        ).status()
                    )
                    color_tag = self.color_tag(status)
                    print("{2} {0:<12} {1:>20} ({3})".format(
                        "("+sub_object.object_type()+")",
                        sub_path,
                        "[{}]".format(index),
                        colorize(status, color_tag)
                    ))
                else:
                    print(
                        "{2} {0:<12} {1:>20}".format(
                            "(" + sub_object.object_type() + ")",
                            sub_path,
                            "[{}]".format(index)
                        )
                    )

        total = len(sub_objects)
        predecessors = self.predecessors()
        if predecessors and show_predecessors:
            print(colorize("o--> Predecessors:", "title0"))
            for index, pred_object in enumerate(predecessors):
                alias = self.path_to_alias(pred_object.invariant_path())
                order = "[{}]".format(total+index)
                pred_path = pred_object.invariant_path()
                obj_type = "("+pred_object.object_type()+")"
                print("{2} {0:<12} {3:>10}: @/{1:<20}".format(
                    obj_type, pred_path, order, alias
                ))

        total += len(predecessors)
        successors = self.successors()
        if successors and show_successors:
            print(colorize("-->o Successors:", "title0"))
            for index, succ_object in enumerate(successors):
                alias = self.path_to_alias(succ_object.invariant_path())
                order = "[{}]".format(total+index)
                succ_path = (
                    succ_object.invariant_path()
                )
                obj_type = "("+succ_object.object_type()+")"
                print("{2} {0:<12} {3:>10}: @/{1:<20}".format(
                    obj_type, succ_path, order, alias
                ))

    def copy_to(self, new_path):
        """ Copy the current objects and its containings to a new path.
        """
        queue = self.sub_objects_recursively()
        # Make sure the related objects are all impressed
        for obj in queue:
            if obj.object_type() != "task" and obj.object_type() != "algorithm":
                continue
            if not obj.is_impressed_fast():
                obj.impress()
        shutil.copytree(self.path, new_path)

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

        # Deal with the impression
        for obj in queue:
            # Calculate the absolute path of the new directory
            norm_path = normpath(f"{new_path}/{self.relative_path(obj.path)}")
            if obj.object_type() == "directory":
                continue
            new_object = vobj.VObject(norm_path)
            new_object.impress()

    def move_to(self, new_path):
        """ move to another path
        """
        queue = self.sub_objects_recursively()

        # Make sure the related objects are all impressed
        all_impressed = True
        for obj in queue:
            if obj.object_type() != "task" and obj.object_type() != "algorithm":
                continue
            if not obj.is_impressed_fast():
                all_impressed = False
                print("The {} {} is not impressed, please impress it and try again".format(obj.object_type(), obj))
        if not all_impressed:
            return
        shutil.copytree(self.path, new_path)

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

        # Deal with the impression
        for obj in queue:
            # Calculate the absolute path of the new directory
            if obj.object_type() == "directory":
                continue
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )
            new_object = vobj.VObject(norm_path)

        if self.object_type() == "directory":
            norm_path = normpath(
                join(new_path, self.relative_path(obj.path))
            )

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
