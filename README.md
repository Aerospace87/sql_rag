## Overview

This repo contains a SQL RAG implemented via:

* LlamaIndex
* HuggingFace
* FastAPI
* PostgresSQL

A podman pod is used to orchestrate the different containers:

1. postgres (SQL Database)
2. mlflow (Mlflow)
3. sql_rag_dev (Web App)
