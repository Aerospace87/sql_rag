#/bin/bash

# Inform the user abut the type of mode to create the pod: dev or prod.
# Creation of a pod named pod_rag_dev. Note that the option --network host
# should be used only for dev and not prod because shares the host network entirely
# with the pod and is insecure. In prod we should use port mapping like -p 543:5432
if [ $1 == "dev" ]; then
    echo "Development mode !"
    podman pod create --network host pod_rag_dev
elif [ $1 == "prod" ]; then
    echo "Production mode !"
    podman pod create -p 8000:8000 -p 5432:5432 pod_rag_dev
else
    echo "Mode $1 not permitted !"
    exit 1
fi

# Creation of a container for postgres db included in the pod
podman run -ti -d \
--name postgres_db_dev \
--pod pod_rag_dev \
--secret pg_db,type=env,target=POSTGRES_DB \
--secret pg_password,type=env,target=POSTGRES_PASSWORD \
--secret pg_user,type=env,target=POSTGRES_USER \
-v ./postgres_container/data:/var/lib/postgresql/18/docker \
postgres_rag_dev

# Creation of the container sql_rag_dev for the webapp
# The volume webapp contain the source code of the app to test source easily when a change occurs
podman run -ti -d \
--name sql_rag_dev \
--pod pod_rag_dev \
--secret hf_token,type=env,target=HF_TOKEN \
--secret pg_db,type=env,target=pg_db \
--secret pg_host,type=env,target=pg_host \
--secret pg_password,type=env,target=pg_password \
--secret pg_port,type=env,target=pg_port \
--secret pg_user,type=env,target=pg_user \
-v ./webapp_container/webapp:/webapp \
localhost/sql_rag_dev

# Show the pod created
podman pod ls

# Show the containers inside the pod
podman ps