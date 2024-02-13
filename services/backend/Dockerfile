# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.1-slim-bookworm

RUN apt-get update && apt-get install -y \
	postgresql-client \
	libpq-dev \
	openssl

RUN mkdir -p /backend/ssl

RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
    -out /backend/ssl/certificate.crt \
    -keyout /backend/ssl/certificate.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# CMD ["daphne", \
# 	"-e", \
# 	"ssl:8000:privateKey=/backend/ssl/certificate.key:certKey=/backend/ssl/certificate.crt", \
# 	"backend.asgi:application"]

# CMD ["daphne", \
#     "-e", "ssl:8000:privateKey=/backend/ssl/certificate.crt:certKey=/backend/ssl/certificate.key", \
# 	"--websocket_timeout=300", "--websocket_connect_timeout=100", \
#     "backend.asgi:application", \
#     "-v", "3"]
