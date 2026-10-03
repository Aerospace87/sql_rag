## Overview

This repo contains a SQL RAG Agent implemented via:

* LlamaIndex
* HuggingFace
* FastAPI
* PostgresSQL

The app runs writing in the browser the endpoint http://localhost:8000/predict/Question and returns a json answer provided by FastAPI. Tracing, observation and evaluation of the agent is performed on mlflow running on http://localhost:5001.

A podman pod is used to orchestrate the different containers:

1. postgres (SQL Database)
2. mlflow (Mlflow)
3. sql_rag_dev (Web App)
