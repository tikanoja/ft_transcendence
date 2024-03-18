# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.1-slim-bookworm

RUN apt-get update && apt-get install -y \
	postgresql-client \
	libpq-dev \
	openssl

RUN mkdir -p /transcendence/ssl

RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
    -out /transcendence/ssl/certificate.crt \
    -keyout /transcendence/ssl/certificate.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

WORKDIR /transcendence

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh

# Having this enabled causes an error... Uncomment and check 'docker logs database_c'
ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# CMD ["daphne", \
# 	"-e", \
# 	"ssl:8000:privateKey=/transcendence/ssl/certificate.key:certKey=/transcendence/ssl/certificate.crt", \
# 	"transcendence.asgi:application"]

# CMD ["daphne", \
#     "-e", "ssl:8000:privateKey=/transcendence/ssl/certificate.crt:certKey=/transcendence/ssl/certificate.key", \
# 	"--websocket_timeout=300", "--websocket_connect_timeout=100", \
#     "transcendence.asgi:application", \
#     "-v", "3"]
