'''
To test:
    utils/csys.py
      + generate_uuid
      + abspath
      + project_path
      + dir_mtime
      + md5sum
      + daemon_path
      + profile_path
      + storage_path
      + local_config_path
      + local_config_dir
      + mkdir
      + copy
      + list_dir
      + rm_tree
      + copy_tree
      + exists
      + make_archive
      + unpack_archive
      + strip_path_string
      + refine_path
      + walk
      + tree_excluded
      + special_path_string
      + colorize
      + color_print
      + debug
      + remove_cache
'''
import Chern.utils.csys as csys
import os
import prepare

def test_generate_uuid():
    print("------------")
    print("Testing generate_uuid...")
    assert len(csys.generate_uuid()) == 32

def test_abs_path():
    print("------------")
    print("Testing abspath...")
    assert csys.abspath('~/') == csys.abspath('~')

def test_project_path():
    print("------------")
    print("Testing project_path...")
    pwd = os.getcwd()
    # Test 1
    prepare.create_chern_project("demo_genfit")
    assert csys.project_path("demo_genfit") == os.path.join(pwd, "demo_genfit")
    assert csys.project_path("demo_genfit/Fit") == os.path.join(pwd, "demo_genfit")
    assert csys.project_path("demo_genfit/Dummy") is None
    assert csys.project_path(".") is None
    prepare.remove_chern_project("demo_genfit")


def test_dir_mtime():
    print("------------")
    print("Testing dir_mtime...")
    print("Automatically passed")

def test_md5sum():
    print("------------")
    print("Testing md5sum...")
    prepare.create_chern_project("demo_genfit")
    assert csys.md5sum("demo_genfit/Gen/gendata.C") == "b74a43595f1bc0d040e22a3cffc82096"
    prepare.remove_chern_project("demo_genfit")

def test_daemon_path():
    print("------------")
    print("Testing daemon_path...")
    print("Deprecated")

def test_profile_path():
    print("------------")
    print("Testing profile_path...")
    print("Deprecated")

def test_storage_path():
    print("------------")
    print("Testing storage_path...")
    print("Deprecated")

def test_local_config_path():
    print("------------")
    print("Testing local_config_path...")
    home = os.environ['HOME']
    assert csys.local_config_path() == os.path.join(home, ".Chern", "config.json")

def test_local_config_dir():
    print("------------")
    print("Testing local_config_dir...")
    home = os.environ['HOME']
    assert csys.local_config_dir() == os.path.join(home, ".Chern")

def test_mkdir():
    print("------------")
    print("Testing mkdir...")
    prepare.create_chern_project("demo_genfit")
    csys.mkdir("demo_genfit/test")
    assert os.path.exists("demo_genfit/test")
    prepare.remove_chern_project("demo_genfit")

def test_copy():
    print("------------")
    print("Testing copy...")
    prepare.create_chern_project("demo_genfit")
    csys.copy("demo_genfit/Gen/gendata.C", "demo_genfit/gendata.C")
    assert os.path.exists("demo_genfit/gendata.C")
    prepare.remove_chern_project("demo_genfit")

def test_list_dir():
    print("------------")
    print("Testing list_dir...")
    prepare.create_chern_project("demo_genfit")
    print(csys.list_dir("demo_genfit/Gen"))
    assert csys.list_dir("demo_genfit/Gen") == ["gendata.C", ".chern", "chern.yaml"]
    prepare.remove_chern_project("demo_genfit")

def test_rm_tree():
    print("------------")
    print("Testing rm_tree...")
    prepare.create_chern_project("demo_genfit")
    csys.rm_tree("demo_genfit/Gen")
    assert not os.path.exists("demo_genfit/Gen")
    prepare.remove_chern_project("demo_genfit")

def test_copy_tree():
    print("------------")
    print("Testing copy_tree...")
    prepare.create_chern_project("demo_genfit")
    csys.copy_tree("demo_genfit/Gen", "demo_genfit/Gen2")
    assert os.path.exists("demo_genfit/Gen2")
    prepare.remove_chern_project("demo_genfit")

def test_exists():
    print("------------")
    print("Testing exists...")
    prepare.create_chern_project("demo_genfit")
    assert csys.exists("demo_genfit/Gen/gendata.C")
    assert not csys.exists("demo_genfit/Gen/gendata.h")
    prepare.remove_chern_project("demo_genfit")

def test_make_archive():
    print("------------")
    print("Testing make_archive...")
    prepare.create_chern_project("demo_genfit")
    csys.make_archive("demo_genfit/Gen", "demo_genfit/Gen.tar.gz")
    assert os.path.exists("demo_genfit/Gen.tar.gz")
    prepare.remove_chern_project("demo_genfit")

def test_unpack_archive():
    print("------------")
    print("Testing unpack_archive...")
    prepare.create_chern_project("demo_genfit")
    csys.make_archive("demo_genfit/Gen", "demo_genfit/Gen")
    csys.unpack_archive("demo_genfit/Gen.tar.gz", "demo_genfit/Gen2")
    assert os.path.exists("demo_genfit/Gen2")
    prepare.remove_chern_project("demo_genfit")

def test_strip_path_string():
    print("------------")
    print("Testing strip_path_string...")
    assert csys.strip_path_string("demo_genfit/Gen/") == "demo_genfit/Gen"

def test_refine_path():
    print("------------")
    home = os.environ['HOME']
    print("Testing refine_path...")
    assert csys.refine_path("~/demo_genfit/Gen/gendata.C", home) == os.path.join(home, "demo_genfit/Gen/gendata.C")

def test_walk():
    print("------------")
    print("Testing walk...")
    return
    prepare.create_chern_project("demo_genfit")
    assert len(csys.walk("demo_genfit/Gen")) == 2
    prepare.remove_chern_project("demo_genfit")

def test_tree_excluded():
    print("------------")
    print("Testing tree_excluded...")
    return
    prepare.create_chern_project("demo_genfit")
    assert csys.tree_excluded("demo_genfit/Gen") == []
    prepare.remove_chern_project("demo_genfit")

def test_special_path_string():
    print("------------")
    print("Testing special_path_string...")
    print("Deprecated")
    return
    assert csys.special_path_string("demo_genfit/Gen/gendata.C") == "demo_genfit/Gen/gendata.C"

def test_colorize():
    print("------------")
    print("Testing colorize...")
    assert csys.colorize("test", "warning") == "\033[31mtest\033[m"

def test_color_print():
    print("------------")
    print("Testing color_print...")
    csys.color_print("test", "red")

def test_debug():
    print("------------")
    print("Testing debug...")
    csys.debug("test")

def test_remove_cache():
    print("------------")
    print("Testing remove_cache...")
    print("Deprecated")
    return
    prepare.create_chern_project("demo_genfit")
    csys.remove_cache("demo_genfit")
    assert not os.path.exists("demo_genfit/.Chern")
    prepare.remove_chern_project("demo_genfit")

if __name__ == '__main__':
    funcs = [test_generate_uuid, test_abs_path, test_project_path, test_dir_mtime, test_md5sum, test_daemon_path, test_profile_path, test_storage_path, test_local_config_path, test_local_config_dir, test_mkdir, test_copy, test_list_dir, test_rm_tree, test_copy_tree, test_exists, test_make_archive, test_unpack_archive, test_strip_path_string, test_refine_path, test_walk, test_tree_excluded, test_special_path_string, test_colorize, test_color_print, test_debug, test_remove_cache]
    for func in funcs:
        func()
    print('All tests passed!')

