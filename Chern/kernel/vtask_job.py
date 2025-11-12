""" JobManager class for managing tasks
"""
import os
from logging import getLogger

from .chern_communicator import ChernCommunicator
from ..utils import csys
from .vtask_core import Core

logger = getLogger("ChernLogger")

class JobManager(Core):
    """ JobManager class for managing tasks"""

    def kill(self):
        """ Kill the task
        """
        cherncc = ChernCommunicator.instance()
        cherncc.kill(self.impression())

    def run_status(self, runner="none"): # pylint: disable=unused-argument
        """ Get the run status of the job"""
        # FIXME duplicated code
        cherncc = ChernCommunicator.instance()
        environment = self.environment()
        if environment == "rawdata":
            md5 = self.input_md5()
            dite_md5 = cherncc.sample_status(self.impression())
            if dite_md5 == md5:
                return "finished"
            return "unsubmitted"
        return cherncc.status(self.impression())

    # Communicator Interaction Methods
    def collect(self):
        """ Collect the results of the job"""
        cherncc = ChernCommunicator.instance()
        cherncc.collect(self.impression())

    def display(self, filename):
        """ Display the file"""
        cherncc = ChernCommunicator.instance()
        # Open the browser to display the file
        cherncc.display(self.impression(), filename)

    def impview(self):
        """ Open browser to view the impression"""
        cherncc = ChernCommunicator.instance()
        return cherncc.impview(self.impression())

    def export(self, filename, output_file):
        """ Export the file"""
        cherncc = ChernCommunicator.instance()
        output_file_path = cherncc.export(
            self.impression(), filename, output_file
            )
        if output_file_path == "NOTFOUND":
            logger.error(
                "File %s not found in the job %s",
                filename, self.impression()
            )

    def send_data(self, path):
        """ Send data to the job"""
        cherncc = ChernCommunicator.instance()
        cherncc.deposit_with_data(self.impression(), path)

    def workaround_preshell(self) -> (tuple[bool, str]):
        """ Pre-shell workaround"""
        cherncc = ChernCommunicator.instance()
        status = cherncc.dite_status()
        if status != "connected":
            return (False, "")
        # Check whether all the preceding jobs are finished
        for pre in self.inputs():
            if not pre.is_impressed_fast():
                return (False, f"Preceding job {pre} is not impressed")
            pre_status = pre.job_status()
            if pre_status != "finished":
                return (False, f"Preceding job {pre} is not finished")
            cherncc.collect(pre.impression())

        # make a temporal directory for data deposit
        temp_dir = csys.create_temp_dir(prefix="chernws_")
        # copy the data to the temporal directory
        file_list = csys.tree_excluded(self.path)
        print(file_list)
        for dirpath, _, filenames in file_list:
            for f in filenames:
                full_path = os.path.join(self.project_path(), self.invariant_path(), dirpath, f)
                rel_path = os.path.relpath(full_path, self.path)
                dest_path = os.path.join(temp_dir, rel_path)
                csys.copy(full_path, dest_path)

        # Create the temporal directory and copy the data there
        for pre in self.inputs():
            pre_temp_dir = csys.create_temp_dir(prefix="chernimp_")
            outputs = cherncc.output_files(pre.impression())
            print(pre_temp_dir)
            csys.mkdir(os.path.join(pre_temp_dir, "outputs"))
            for f in outputs:
                cherncc.export(pre.impression(), f"{f}", os.path.join(pre_temp_dir, "outputs", f))
            alias = self.path_to_alias(pre.invariant_path())
            print(f"Linking preceding job {pre} to {alias}")
            # Make a symlink
            csys.symlink(
                os.path.join(pre_temp_dir),
                os.path.join(temp_dir, alias),
            )

        algorithm = self.algorithm()
        if algorithm:
            alg_temp_dir = csys.create_temp_dir(prefix="chernws_")
            file_list = csys.tree_excluded(algorithm.path)
            print(file_list)
            for dirpath, _, filenames in file_list:
                for f in filenames:
                    full_path = os.path.join(self.project_path(), algorithm.invariant_path(), dirpath, f)
                    rel_path = os.path.relpath(full_path, algorithm.path)
                    dest_path = os.path.join(alg_temp_dir, rel_path)
                    csys.copy(full_path, dest_path)
            csys.symlink(
                os.path.join(alg_temp_dir),
                os.path.join(temp_dir, "code"),
            )

        return (True, temp_dir)

    def workaround_postshell(self, path) -> bool:
        """ Post-shell workaround"""
        return True
