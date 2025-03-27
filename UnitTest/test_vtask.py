import Chern.kernel.vtask as vtsk
import os
import prepare
from colored import Fore, Style

def test_setting():
    print("------------")
    print(Fore.BLUE+"Testing setting..."+Style.RESET)
    prepare.create_chern_project("demo_complex")
    os.chdir("demo_complex")
    obj_tsk = vtsk.VTask(os.getcwd()+"/tasks/taskAna1")


    assert obj_tsk.environment() == "reanahub/reana-env-root6:6.18.04"
    assert obj_tsk.memory_limit() == "256Mi"
    assert obj_tsk.parameters() == ([], {})
    assert obj_tsk.auto_download() is True
    assert obj_tsk.default_runner() == "local"

    print(obj_tsk.env_validated())
    print(obj_tsk.validated())

    obj_tsk.set_environment("new_env")
    print(obj_tsk.environment())
    assert obj_tsk.environment() == "new_env"
    obj_tsk.set_memory_limit("1Gi")
    assert obj_tsk.memory_limit() == "1Gi"
    obj_tsk.add_parameter("param1", "value1")
    assert obj_tsk.parameters() == (["param1"], {"param1": "value1"})
    obj_tsk.remove_parameter("param1")
    assert obj_tsk.parameters() == ([], {})
    obj_tsk.set_auto_download(False)
    assert obj_tsk.auto_download() is False
    obj_tsk.set_default_runner("new_runner")
    assert obj_tsk.default_runner() == "new_runner"


    os.chdir("..")
    prepare.remove_chern_project("demo_complex")



def test_init():
    print("------------")
    print(Fore.BLUE+"Testing Init Commands..."+Style.RESET)

    prepare.create_chern_project("demo_complex")
    os.chdir("demo_complex")
    obj_tsk = vtsk.VTask(os.getcwd()+"/tasks/taskAna1")

    assert obj_tsk.__str__() == "tasks/taskAna1"
    assert obj_tsk.__repr__() == "tasks/taskAna1"
    assert obj_tsk.invariant_path() == "tasks/taskAna1"
    assert obj_tsk.object_type() == "task"
    assert obj_tsk.is_zombie() is False
    assert obj_tsk.is_task_or_algorithm() is True

    os.chdir("..")
    prepare.remove_chern_project("demo_complex")

def test_file():
    print("------------")
    print(Fore.BLUE+"Testing File Operation..."+Style.RESET)

    obj_tsk = vtsk.VTask(os.getcwd()+"/tasks/taskAna1")
    obj_tsk.move_to(os.getcwd()+"/tasks/TASKANA1")

    print(obj_tsk.invariant_path())



if __name__ == "__main__":
    # warm_up()
    test_init()
    test_setting()
    test_file()
    print("All tests passed!")

