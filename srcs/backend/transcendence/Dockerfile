# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.1-slim-bookworm

RUN apt-get update && apt-get install -y \
	postgresql-client \
	libpq-dev \
	openssl \
    build-essential 

RUN mkdir -p /transcendence/ssl \
	mkdir -p /transcendence/media
RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
    -out /transcendence/ssl/certificate.crt \
    -keyout /transcendence/ssl/certificate.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

COPY ./conf/requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip -r /tmp/requirements.txt

WORKDIR /transcendence

ENTRYPOINT ["./start.sh"]
