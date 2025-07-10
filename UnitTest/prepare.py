'''
    Generate or remove the data for the project.
'''
import shutil

def create_chern_project(src):
    '''
    Create the project directory.
    '''
    # Check whether the directory already exists.
    if shutil.os.path.exists(src):
        print(f"Directory {src} already exists. Remove it first.")
        shutil.rmtree(src)
    # Copy the folder from data to the directory.
    shutil.copytree("data/"+src, src)

def remove_chern_project(src):
    '''
    Remove the project directory.
    '''
    # Remove the folder.
    shutil.rmtree(src)
