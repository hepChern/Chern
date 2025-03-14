import Chern.kernel.VObject as vobj
import os
import prepare
from colored import Fore, Style


def test_impression():
    print("------------")
    print(Fore.BLUE+"Testing impression..."+Style.RESET)

    print("#1 Test whether the change could be identified.")
    prepare.create_chern_project("demo_genfit_new")
    os.chdir("demo_genfit_new")
    obj_gen = vobj.VObject(os.getcwd()+"/Gen")
    obj_gentask = vobj.VObject(os.getcwd()+"/GenTask")
    obj_fit = vobj.VObject(os.getcwd()+"/Fit")
    obj_fitTask = vobj.VObject(os.getcwd()+"/FitTask")

    assert obj_gen.is_impressed() is False
    assert obj_gentask.is_impressed() is False
    assert obj_fit.is_impressed() is True
    assert obj_fitTask.is_impressed() is False

    os.chdir("..")
    prepare.remove_chern_project("demo_genfit_new")

    print("#2 Test whether the impression could be done.")
    prepare.create_chern_project("demo_genfit_new")
    os.chdir("demo_genfit_new")
    obj_gen = vobj.VObject(os.getcwd()+"/Gen")
    obj_gentask = vobj.VObject(os.getcwd()+"/GenTask")
    obj_fit = vobj.VObject(os.getcwd()+"/Fit")
    obj_fitTask = vobj.VObject(os.getcwd()+"/FitTask")
    obj_fitTask.impress()

    assert obj_gen.is_impressed() == True
    assert obj_gentask.is_impressed() == True
    assert obj_fit.is_impressed() == True
    assert obj_fitTask.is_impressed() == True

    os.chdir("..")
    prepare.remove_chern_project("demo_genfit_new")


def test_core():
    print("------------")
    print(Fore.BLUE+"Testing Core Commands..."+Style.RESET)
    print(Fore.YELLOW+"[Warning] the illegal operations of the following commands are not tested.")
    print("copy_to illegal: copy to a path that already exists.")
    print("move_to illegal: move to a path that already exists.")
    print("rm illegal: remove a path that does not exist.")
    print(Style.RESET)
    # Switch to the normal color

    # Need to test ls, copy_to, move_to, rm, sub_objects
    # The test of ls is omitted here.
    prepare.create_chern_project("demo_complex")
    os.chdir("demo_complex")

    print("#1 Test the sub_objects")
    obj_top = vobj.VObject(os.getcwd())
    assert [obj.invariant_path() for obj in obj_top.sub_objects()] == ['tasks', 'includes', 'code']

    obj_includes = vobj.VObject(os.getcwd()+"/includes")
    assert [obj.invariant_path() for obj in obj_includes.sub_objects()] == ['includes/inc', 'includes/inc2']

    obj_task1 = vobj.VObject(os.getcwd()+"/tasks/taskAna2")
    assert [obj.invariant_path() for obj in obj_task1.sub_objects()] == []

    print("#2 Test the copy_to")
    obj_folder = vobj.VObject(os.getcwd()+"/tasks")
    obj_folder.copy_to("tasksDuplicate")
    assert [obj.invariant_path() for obj in obj_top.sub_objects()] == ['tasks', 'includes', 'code', 'tasksDuplicate']
    assert vobj.VObject(os.getcwd()+"/tasksDuplicate").is_zombie() is False
    assert vobj.VObject(os.getcwd()+"/tasksDuplicate/taskAna1").is_impressed() is True
    assert vobj.VObject(os.getcwd()+"/tasksDuplicate/taskAna2").is_impressed() is True
    assert vobj.VObject(os.getcwd()+"/tasksDuplicate/taskQA").is_impressed() is True
    assert vobj.VObject(os.getcwd()+"/tasksDuplicate/taskGen").is_impressed() is True
    # Check the successors and predecessors
    obj_task1 = vobj.VObject(os.getcwd()+"/tasksDuplicate/taskAna1")
    assert [obj.invariant_path() for obj in obj_task1.successors()] == ['tasksDuplicate/taskAna2']
    assert [obj.invariant_path() for obj in obj_task1.predecessors()] == ['tasksDuplicate/taskGen']

    # Record the impression of the tasks
    imp_taskAna1 = vobj.VObject(os.getcwd()+"/tasks/taskAna1").impression().__str__()
    imp_taskAna2 = vobj.VObject(os.getcwd()+"/tasks/taskAna2").impression().__str__()
    imp_taskQA = vobj.VObject(os.getcwd()+"/tasks/taskQA").impression().__str__()
    imp_taskGen = vobj.VObject(os.getcwd()+"/tasks/taskGen").impression().__str__()
    obj_folder = vobj.VObject(os.getcwd()+"/tasks")
    obj_folder.move_to("tasksMoved")
    # ['includes', 'code', 'tasksMoved', 'tasksDuplicate']
    assert [obj.invariant_path() for obj in obj_top.sub_objects()] == ['includes', 'code', 'tasksMoved', 'tasksDuplicate']
    assert vobj.VObject(os.getcwd()+"/tasksMoved").is_zombie() is False
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskAna1").is_impressed() is True
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskAna2").is_impressed() is True
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskQA").is_impressed() is True
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskGen").is_impressed() is True
    # Check the impression not changed after moving
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskAna1").impression().__str__() == imp_taskAna1
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskAna2").impression().__str__() == imp_taskAna2
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskQA").impression().__str__() == imp_taskQA
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskGen").impression().__str__() == imp_taskGen
    # Check the successors and predecessors
    obj_task1 = vobj.VObject(os.getcwd()+"/tasksMoved/taskAna1")
    # ['tasksMoved/taskAna2']
    # ['tasksMoved/taskGen', 'code/ana1']
    assert [obj.invariant_path() for obj in obj_task1.successors()] == ['tasksMoved/taskAna2']
    assert [obj.invariant_path() for obj in obj_task1.predecessors()] == ['tasksMoved/taskGen', 'code/ana1']

    obj_folder = vobj.VObject(os.getcwd()+"/tasksMoved")
    obj_folder.rm()
    assert [obj.invariant_path() for obj in obj_top.sub_objects()] == ['includes', 'code', 'tasksDuplicate']
    assert vobj.VObject(os.getcwd()+"/tasksMoved").is_zombie() is True
    assert vobj.VObject(os.getcwd()+"/tasksMoved/taskAna1").is_zombie() is True
    # Check the impression could still be found after removing
    # in demo_complex/.chern/impressions
    assert os.path.exists(os.getcwd()+"/.chern/impressions/{0}".format(imp_taskAna1))
    assert [obj.invariant_path() for obj in vobj.VObject(os.getcwd()+"/code/ana1").successors()] == []

    os.chdir("..")
    prepare.remove_chern_project("demo_complex")


def test_init():
    print("------------")
    print(Fore.BLUE+"Testing Init Commands..."+Style.RESET)

    prepare.create_chern_project("demo_complex")
    os.chdir("demo_complex")
    obj_top = vobj.VObject(os.getcwd())
    obj_alg = vobj.VObject(os.getcwd()+"/code/ana1")
    obj_tsk = vobj.VObject(os.getcwd()+"/tasks/taskAna1")
    obj_err = vobj.VObject(os.getcwd()+"/NotExists")

    assert obj_top.__str__() == "."
    assert obj_alg.__str__() == "code/ana1"
    assert obj_tsk.__str__() == "tasks/taskAna1"
    assert obj_err.__str__() == "NotExists"

    assert obj_top.__repr__() == "."
    assert obj_alg.__repr__() == "code/ana1"
    assert obj_tsk.__repr__() == "tasks/taskAna1"
    assert obj_err.__repr__() == "NotExists"

    assert obj_top.invariant_path() == "."
    assert obj_alg.invariant_path() == "code/ana1"
    assert obj_tsk.invariant_path() == "tasks/taskAna1"
    assert obj_err.invariant_path() == "NotExists"

    assert obj_top.object_type() == "project"
    assert obj_alg.object_type() == "algorithm"
    assert obj_tsk.object_type() == "task"
    assert obj_err.object_type() == ""

    assert obj_top.is_zombie() is False
    assert obj_alg.is_zombie() is False
    assert obj_tsk.is_zombie() is False
    assert obj_err.is_zombie() is True

    print(obj_alg.is_task_or_algorithm())
    assert obj_top.is_task_or_algorithm() is False
    assert obj_alg.is_task_or_algorithm() is True
    assert obj_tsk.is_task_or_algorithm() is True
    assert obj_err.is_task_or_algorithm() is False

    os.chdir("..")
    prepare.remove_chern_project("demo_complex")


if __name__ == "__main__":
    # warm_up()
    test_init()
    test_core()
    test_impression()
    print("All tests passed!")

