#/bin/bash
podman run -ti -d \
--network host \
--rm \
--secret hf_token,type=env,target=HF_TOKEN \
--secret pg_db,type=env,target=pg_db \
--secret pg_host,type=env,target=pg_host \
--secret pg_password,type=env,target=pg_password \
--secret pg_port,type=env,target=pg_port \
--secret pg_user,type=env,target=pg_user \
--name sql_rag_dev -v ./webapp:/webapp localhost/sql_rag_dev