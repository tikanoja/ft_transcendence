# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.1-slim-bookworm

RUN apt-get update && apt-get install -y \
	postgresql-client \
	libpq-dev \
	openssl

RUN mkdir -p /user_service/ssl

RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
    -out /user_service/ssl/certificate.crt \
    -keyout /user_service/ssl/certificate.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

WORKDIR /user_service

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh

# Having this enabled causes an error... Uncomment and check 'docker logs database_c'
# ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# CMD ["daphne", \
# 	"-e", \
# 	"ssl:8000:privateKey=/user_service/ssl/certificate.key:certKey=/user_service/ssl/certificate.crt", \
# 	"user_service.asgi:application"]

# CMD ["daphne", \
#     "-e", "ssl:8000:privateKey=/user_service/ssl/certificate.crt:certKey=/user_service/ssl/certificate.key", \
# 	"--websocket_timeout=300", "--websocket_connect_timeout=100", \
#     "user_service.asgi:application", \
#     "-v", "3"]
