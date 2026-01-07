#/bin/bash

podman run -ti -d \
--name postgres_db_dev \
--secret pg_db,type=env,target=POSTGRES_DB \
--secret pg_password,type=env,target=POSTGRES_PASSWORD \
--secret pg_user,type=env,target=POSTGRES_USER \
-p 5432:5432 \
-v ./data:/var/lib/postgresql/18/docker \
postgres_rag_dev

#pg_restore -U aerospace -d AlphaShop -v "AlphaShop.sql"


