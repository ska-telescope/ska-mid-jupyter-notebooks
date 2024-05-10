# SKA Mid Jupyter Notebooks

[![Binder](https://k8s.miditf.internal.skao.int/binderhub/badge_logo.svg)](https://k8s.miditf.internal.skao.int/binderhub/v2/gl/ska-telescope%2Fska-mid-jupyter-notebooks/main)

## Purpose

This repo contains notebooks intended to be executed against the Mid-ITF. These notebooks can be used to make demos easier to design and follow, as well as make them more repeatable for validation. Some more general notebooks can also be used as onboarding tools, to demonstrate how to interact with Mid-ITF, without having to do much set-up.

## Using Notebooks

Most notebooks in this repository were developed with [VSCode's Jupyter Notebook functionality](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) in mind, but can also be run via [JupyterLab](https://github.com/jupyterlab/jupyterlab-desktop). To run a notebook, it is recommended to use a [Python Virtual Environment](https://docs.python.org/3/library/venv.html), in order to keep libraries and versioning organized. A non-venv Python interpreter can also be used, but users will have to manage libraries and Python versions manually. 

## Contributing

### Prerequisites

When writing notebooks, be sure to run `git submodule init` and `git submodule update`. This will pull the latest .make directory for this repository, allowing full use of Make commands. In a Python venv, use `poetry install` to grab the libraries required by this repository itself. 

### Writing Notebooks

When creating/updating a notebook, the following should be referenced: 
- [The SKAO code guidelines for Jupyter.](https://developer.skatelescope.org/en/latest/tools/codeguides/jupyter-notebook-codeguide.html)
- [The notebook template in this repository.](notebooks/template/notebook_template.ipynb).
- If writing configs, refer to the [relevant MID schemas.](https://developer.skao.int/projects/ska-telmodel/en/stable/schemas/midcbf/ska-mid-cbf.html)

### Committing  

When pushing to the remote, run `make notebook-lint` to preview any linting changes. To run the linter and make automatic changes to your notebooks run `make notebook-format`.

