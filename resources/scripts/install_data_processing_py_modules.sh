#!/bin/bash

#Downgrade protobuf to 3.20.1
sed -i '/\[tool.poetry.dependencies\]/a protobuf = "3.20.1"' ../../pyproject.toml
#update the lock file
cd ../../ && poetry lock --no-update && poetry install

#Prepare to install casadata module.
#The following directory structure is needed for casadata to work.
#It is the download location of the casadata
mkdir -p ~/.casa && mkdir -p ~/.casa/data

pip install casadata && pip install casatasks && pip install casaviewer

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

echo "*** Casa modules installed with success***"