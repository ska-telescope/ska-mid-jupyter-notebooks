#!/bin/bash

cd ../../

#Prepare to install casadata module.
#The following directory structure is needed for casadata to work.
#It is the download location of the casadata
mkdir -p ~/.casa/data

#Add required python libraries
poetry add protobuf=="3.20.1" 
poetry add casadata 
poetry add casatasks
poetry add casaviewer

#update the lock file
poetry lock --no-update && poetry install

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
echo "*** Casa modules installed with success. ***"