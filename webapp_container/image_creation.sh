#/bin/bash

# Building the base image with base requirements.
podman build -f Containerfile.base -t sql_rag_dev_base

# Building the final image with extra requirements
podman build -t sql_rag_dev .
