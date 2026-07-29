#/bin/bash

# Image creation
podman build -t mlflow_img .

# Container creation with name "mlflow"
podman run -d --rm \
-p 5001:5001 \
--name mlflow \
-v sqlite:/sqlite \
mlflow_img

# Show all active containers
podman ps
