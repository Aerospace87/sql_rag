#/bin/bash
podman build -f Containerfile.base -t sql_rag_dev_base

podman build -t sql_rag_dev .
