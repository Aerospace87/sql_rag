#/bin/bash
#podman run -ti -d \
#--network host \
#--rm \
#--secret hf_token,type=env,target=HF_TOKEN \
#--secret pg_db,type=env,target=pg_db \
#--secret pg_host,type=env,target=pg_host \
#--secret pg_password,type=env,target=pg_password \
#--secret pg_port,type=env,target=pg_port \
#--secret pg_user,type=env,target=pg_user \
#--name sql_rag_dev -v ./webapp:/webapp localhost/sql_rag_dev


# Image creation
podman build -t mlflow_img .

# Container creation with name "mlflow"
podman run -d -p 5001:5001 --rm --name mlflow mlflow_img

# Show all active containers
podman ps
