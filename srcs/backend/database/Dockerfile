FROM postgres:16.0-bookworm

# COPY ./conf/* /var/lib/postgresql/data/

COPY ./init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
