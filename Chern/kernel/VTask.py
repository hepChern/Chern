""" The VTask class
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Methods:
        + helpme:
            Print the helpme of the task
        + ls:
            First call the general ls and then print some other useful information:
            parameters, status, outputs, algorithms
        + output_files:
            Get the information of the output_files from ChernCommunicator
        + get_file:
            Get file??? from ChernCommunicator

        + inputs:
        + outputs:

        + submit
            Submit the job to server. Through ChernCommunicator.
        + resubmit
            Resubmit the job to server. Through ChernCommunicator.
        + view
        + cp
            Copy the output to some directory
        + remove
            Remove the task.
        + jobs
            Query the jobs of the task throught ChernCommunicator.

        + view
            Open the file through ChernCommunicator. This is quite temporatory. Because it can only open local file.

        + is_submitted:
            Judge whether the task is submitted or not. Ask this information from ChernCommunicator.

        + output_md5:
            Read the md5 of the output directory

        + add_parameter
        + remove_parameter:
            Add/Remove parameter, should deal the problem of missing parameter/parameter already there.

        + add_input
            Add input to the task(with alias), print something, maybe changed later.
        + remove_input
            Remove input of the task through alias.

        + add_algorithm
            Add the algorithm correspnding to the task. if already has algorithm, replace the old one and print the message. Maybe changed later
            because I do not want to print anything in the kernel.
        + remove_algorithm
            Remove the algorithm corresponding to the task. if nothing to remove it print the message. Maybe changed later because I do
            not want to print anything in the kernel.
        + algorithm
            Return the algorithm corresponding to this task. If the task is not related to an algorithm, return None.

        + container
            Return the container corresponding the top impression.
        + add_source
            Make a new task, with raw data.

        + add_output
            ABANDONED
        + remove_output
            ABANDONED
        ===================
        Inherited from VObject
        + __init__
        + __str__, __repr__
        + invariant_path, relative_path
        + object_type, is_zombine
        + color_tag
        + ls
        + copy_to, clean_impressions/flow
        + rm
        + move_to
        + alias(and related)
        + add/remove_arc_from/to
        + (has)successor/predecessors(s)
        + doctor
        + pack(and related)
        + impression(and related)

"""
import os
import uuid
import subprocess
from Chern.kernel.VObject import VObject
# from Chern.kernel.VContainer import VContainer
from Chern.kernel import VAlgorithm
from Chern.utils import utils
from Chern.utils import metadata
from Chern.utils.pretty import colorize
from Chern.utils import csys

from Chern.kernel.ChernCache import ChernCache
from Chern.kernel.ChernCommunicator import ChernCommunicator
from logging import getLogger

cherncache = ChernCache.instance()
logger = getLogger("ChernLogger")

class VTask(VObject):
    def helpme(self, command):
        from Chern.kernel.Helpme import task_helpme
        print(task_helpme.get(command, "No such command, try ``helpme'' alone."))

    def ls(self, show_readme=True, show_predecessors=True, show_sub_objects=True, show_status=True, show_successors=False):
        super(VTask, self).ls(show_readme, show_predecessors, show_sub_objects, show_status, show_successors)
        parameters, values = self.parameters()
        if parameters != []:
            print(colorize("---- Parameters:", "title0"))
        for parameter in parameters:
            print(parameter, end=" = ")
            print(values[parameter])

        if show_status:
            status = self.status()
            if status == "new":
                status_color = "normal"
            elif status == "impressed":
                status_color = "success"

            status_str = colorize("["+status+"]", status_color)

            if status == "impressed":
                run_status = self.run_status()
                if (run_status == "unsubmitted"):
                    status_color = "warning"
                else:
                    status_color = "success"
                status_str += colorize("["+run_status+"]", status_color) 
            print(colorize("**** STATUS:", "title0"), status_str)


        if self.is_submitted():
            print(colorize("---- Files:", "title0"))
            files = self.output_files()
            if files != []:
                files.sort()
                max_len = max([len(s) for s in files])
                columns = os.get_terminal_size().columns
                nfiles = columns // (max_len+4+7)
                for i, f in enumerate(files):
                    if not f.startswith(".") and f != "README.md":
                        print(("local:{:<"+str(max_len+4)+"}").format(f), end="")
                        if (i+1)%nfiles == 0:
                            print("")
                print("")

        if self.algorithm() is not None:
            print(colorize("---- Algorithm files:", "title0"))
            files = os.listdir(self.algorithm().path)
            if files == []: return
            files.sort()
            max_len = max([len(s) for s in files])
            columns = os.get_terminal_size().columns
            nfiles = columns // (max_len+4+11)
            for i, f in enumerate(files):
                if f.startswith("."): continue
                if f == "README.md": continue
                if f == "chern.yaml": continue
                print(("algorithm:{:<"+str(max_len+4)+"}").format(f), end="")
                if (i+1)%nfiles == 0: print("")
            print(colorize("---- Commands:", "title0"))
            for command in self.algorithm().commands():
                parameters, values = self.parameters()
                for parameter in parameters:
                    parname = "${" + parameter + "}"
                    command = command.replace(parname, values[parameter])
                print(command)


    def output_files(self):
        # FIXME, to get the output files list
        return []
        cherncc = ChernCommunicator.instance()
        return cherncc.output_files("local", self.impression())

    def get_file(self, filename):
        cherncc = ChernCommunicator.instance()
        return cherncc.get_file("local", self.impression(), filename)

    def inputs(self):
        """ Input data. """
        inputs = filter(lambda x: x.object_type() == "task", self.predecessors())
        return list(map(lambda x: VTask(x.path), inputs))

    def outputs(self):
        """ Output data. """
        outputs = filter(lambda x: x.object_type() == "task", self.successors())
        return list(map(lambda x: VTask(x.path), outputs))

    def resubmit(self, machine = "local"):
        if not self.is_submitted():
            print("Not submitted yet.")
            return
        cherncc.resubmit(self.impression(), machine)

        path = utils.storage_path() + "/" + self.impression()
        csys.rm_tree(path)
        self.submit()

    def view(self, filename):
        if filename.startswith("local:"):
            path = self.get_file("local:", filename[6:])
            if not csys.exists(path):
                print("File: {} do not exists".format(path))
                return
            subprocess.Popen("open {}".format(path), shell=True)

    def cp(self, source, dst):
        if source.startswith("local:"):
            path = self.container().path+"/output/"+source.replace("local:", "").lstrip()
            if not csys.exists(path):
                print("File: {} do not exists".format(path))
                return
            csys.copy(path, dst)

    """
    def remove(self, remove_impression):
        impressions = self.config_file.read_variable("impressions", [])
        impression = self.config_file.read_variable("impression")
        if remove_impression == impression[:8]:
            print("The most recent job is not allowed to remove")
            return
        for im in impressions:
            path = utils.storage_path() + "/" + im
            if not os.path.exists(path):
                continue
            if remove_impression == im[:8]:
                print("Try to remove the job")
                container = VContainer(path)
                container.remove()
                return

    def jobs(self):
        impressions = self.config_file.read_variable("impressions", [])
        output_md5s = self.config_file.read_variable("output_md5s", {})
        if impressions == []:
            return
        impression = self.config_file.read_variable("impression")
        for im in impressions:
            path = utils.storage_path() + "/" + im
            if not os.path.exists(path):
                continue
            if impression == im:
                short = "*"
            else:
                short = " "
            short += im[:8]
            output_md5 = output_md5s.get(im, "")
            if output_md5 != "":
                short += " ({0})".format(output_md5[:8])
            status = VContainer(path).status()
            print("{0:<12}   {1:>20}".format(short, status))
    """

    def stdout(self):
        with open(self.container().path+"/stdout") as f:
            return f.read()

    def stderr(self):
        with open(self.container().path+"/stderr") as f:
            return f.read()

    def is_submitted(self, machine="local"):
        """ Judge whether submitted or not. Return a True or False.
        [FIXME: incomplete]
        """
        if not self.is_impressed_fast():
            return False
        return False

        cherncc = ChernCommunicator.instance()
        if not self.is_impressed_fast():
            return False
        return cherncc.status(self.impression()) != "unsubmitted"


    def output_md5(self):
        output_md5s = self.config_file.read_variable("output_md5s", {})
        return output_md5s.get(self.impression(), "")

    def status(self, consult_id = None, detailed = False):
        """ Consult the status of the object
            There should be only two status locally: new|impressed
        """
        # If it is already asked, just give us the answer
        logger.debug("VTask status: Consulting status of {}".format(self.path))
        if consult_id:
            consult_table = cherncache.status_consult_table
            cid, status = consult_table.get(self.path, (-1,-1))
            if cid == consult_id:
                return status

        if not self.is_impressed_fast():
            if consult_id:
                consult_table[self.path] = (consult_id, "new")
            return "new"

        status = "impressed"
        if consult_id:
            consult_table[self.path] = (consult_id, status)
        return status

    def run_status(self, host = "local"):
        cherncc = ChernCommunicator.instance()
        return cherncc.status(self.impression())

    """
    def container(self):
        path = utils.storage_path() + "/" + self.impression()
        return VContainer(path)
    """

    def add_source(self, path):
        """
        After add source, the status of the task should be done
        """
        md5 = csys.dir_md5(path)
        data_file = metadata.ConfigFile(os.path.join(self.path, "data.json"))
        data_file.write_variable("md5", md5)
        self.impress()
        return

    def add_algorithm(self, path):
        """
        Add a algorithm
        """
        algorithm = self.algorithm()
        if algorithm is not None:
            print("Already have algorithm, will replace it")
            self.remove_algorithm()
        self.add_arc_from(VObject(path))


    def remove_algorithm(self):
        """
        Remove the algorithm
        """
        algorithm = self.algorithm()
        if algorithm is None:
            print("Nothing to remove")
        else:
            self.remove_arc_from(algorithm)

    def algorithm(self):
        """
        Return the algorithm
        """
        predecessors = self.predecessors()
        for pred_object in predecessors:
            if pred_object.object_type() == "algorithm":
                return VAlgorithm.VAlgorithm(pred_object.path)
        return None

    def add_input(self, path, alias):
        """ FIXME: judge the input type
        """
        obj = VObject(path)
        if obj.object_type() != "task":
            print("You are adding {} type object as input. The input is required to be a task.".format(obj.object_type()))
            return

        if self.has_alias(alias):
            print("The alias already exists. The original input and alias will be replaced.")
            project_path = csys.project_path(self.path)
            original_object = VObject(project_path+"/"+self.alias_to_path(alias))
            self.remove_arc_from(original_object)
            self.remove_alias(alias)

        self.add_arc_from(obj)
        self.set_alias(alias, obj.invariant_path())

    def remove_input(self, alias):
        path = self.alias_to_path(alias)
        if path == "":
            print("Alias not found")
            return
        project_path = csys.project_path(self.path)
        obj = VObject(project_path+"/"+path)
        self.remove_arc_from()
        self.remove_alias(alias)


    def add_output(self, file_name):
        """ FIXME: The output is now binding with the task
        """
        outputs = self.read_variable("outputs", [])
        outputs.append(file_name)
        self.write_variable("outputs", outputs)

    def remove_output(self, alias):
        """ FIXME: check existence
        """
        outputs = self.read_variable("outputs", [])
        outputs.append(file_name)
        self.write_variable("outputs", outputs)

    def parameters(self):
        """
        Read the parameters file
        """
        parameters_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        parameters = parameters_file.read_variable("parameters", {})
        return sorted(parameters.keys()), parameters

    def add_parameter(self, parameter, value):
        """
        Add a parameter to the parameters file
        """
        parameters_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        parameters = parameters_file.read_variable("parameters", {})
        parameters[parameter] = value
        parameters_file.write_variable("parameters", parameters)

    def remove_parameter(self, parameter):
        """
        Remove a parameter to the parameters file
        """
        parameters_file = metadata.YamlFile(os.path.join(self.path, "chern.yaml"))
        parameters = parameters_file.read_variable("parameters", {})
        if parameter not in parameters.keys():
            print("Parameter not found")
            return
        parameters.pop(parameter)
        parameters_file.write_variable("parameters", parameters)

def create_task(path):
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(path+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "project" and object_type != "directory":
        return

    csys.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path + "/.chern/config.json")
    config_file.write_variable("object_type", "task")
    task = VObject(path)

    with open(path + "/.chern/README.md", "w") as f:
        f.write("Please write README for task {}".format(task.invariant_path()))

def create_data(path):
    path = utils.strip_path_string(path)
    parent_path = os.path.abspath(path+"/..")
    object_type = VObject(parent_path).object_type()
    if object_type != "project" and object_type != "directory":
        return

    csys.mkdir(path+"/.chern")
    config_file = metadata.ConfigFile(path + "/.chern/config.json")
    config_file.write_variable("object_type", "task")
    task = VObject(path)

    with open(path + "/.chern/README.md", "w") as f:
        f.write("Please write README for task {}".format(task.invariant_path()))

    with open(path + "/validation.txt", "w") as f:
        f.write("""Whenever to fill a new version of the data,
please edit this file and do the: ``impress''.
It is suggestive to write the md5 of the data folder to this file.
md5 =
""")

