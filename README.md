# SKA Mid Jupyter Notebooks

[![Binder](https://k8s.miditf.internal.skao.int/binderhub/badge_logo.svg)](https://k8s.miditf.internal.skao.int/binderhub/v2/gl/ska-telescope%2Fska-mid-jupyter-notebooks/main)

## Purpose

This repo contains notebooks intended to be executed against the Mid-ITF.

## Environment Setup

### Using Dev Container

This repository contains a VS Code development container configuration that can be used to automatically setup a development container for developing and running notebooks in an isolated environment from within VS Code. Follow these steps to use the development container:

1. Open VS Code and add the repository to the Workspace.
2. Click "_Open Remote Window_" in the bottom left corner and select the "Open folder in container..." option.
3. Once VS Code reopens (this may take some time if it is the first time you are building the container) select View > Terminal and run the following command in the terminal: `Poetry install` (this only needs to be done the first time you are running the container, or when python dependencies have been changed in _pyproject.toml_).
This will setup a virtual environment on your host bound to the development container and install all python dependencies.
4. In the top right corner of VS Code click on _Select Kernel_ > _Python Environments_ then select the following path: _.venv/bin/python_
5. If your environment looks similar to the image below, you have performed all the steps correctly and can continue.
![VS Code dev environment](static/images/vscode_dev_container_environment.jpg)

#### Caveat: pre-existing .venv folder

Sometimes you may want to follow step 3 only above _after_ removing the `.venv` folder entirely first - if the virtual environment was for some reason created on your local machine, some of the imports will not work as expected. Simply delete the folder (right-click & delete or `$ rm -rf .venv` in terminal), then run `poetry install`.

## Creating Notebooks

### Importing Steps from Jama System Tests

1. Copy the steps in the table in the _Steps_ section and save them as a CSV file. If the steps include commas internally, consider saving the file using a different delimiter such as a semicolon (;):
![Jama Test Case Export](static/images/jama_export.png)

2. Run the `convert_nb.py` script: `poetry run convertnb $CSV_SOURCE_FILE $NB_DEST_FILE`. Use the delimiter flag to specify an alternate delimiter if your CSV file does not use comma delimiters: `poetry run convertnb $CSV_SOURCE_FILE $NB_DEST_FILE -d ";"`

This will convert each step listed in the Jama test case into a section in the Juypyter Notebook. The _Action_ and _Expected Result_ will be added as a description to that step.
