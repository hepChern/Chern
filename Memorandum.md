# Memorandum for meta data format of Chern v4
## Metadata type 1: (preservable metadata)
This type of metadata is saved in yaml file, and readable by human
### Task
### Data
### Algorithm
## Metadata type 2: (non-preservable metadata)
This type of metadata is saved in json file, not needed to be read by human
### Task
### Data
### Algorithm

---------------------------
Guidance for installing Chern

The project is a python project, therefore, it is strongly recommand to use venv to install the Chern
python -m build
pip install dist/chern-0.0.1-py3-none-any.whl
If you want to install the package in editable mode, you can use the following command:
pip install -e .
