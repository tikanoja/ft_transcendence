# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.1-slim-bookworm

RUN apt-get update && apt-get install -y \
    openssl

#TODO Shouldn't run all this on root, create a restricted user...
#TODO Figure out later along with Daphne
#RUN mkdir -p /ssl
#RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
#    -out /ssl/certificate.crt \
#    -keyout /ssl/certificate.key \
#    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

COPY ./requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip -r /tmp/requirements.txt

## RUN chmod +x entrypoint.sh
## ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "/chat_service/manage.py", "runserver", "0.0.0.0:8002"]

# CMD ["daphne", \
# 	"-e", \
# 	"ssl:8000:privateKey=/chat_service/ssl/certificate.key:certKey=/chat_service/ssl/certificate.crt", \
# 	"chat_service.asgi:application"]

# CMD ["daphne", \
#     "-e", "ssl:8000:privateKey=/chat_service/ssl/certificate.crt:certKey=/chat_service/ssl/certificate.key", \
# 	"--websocket_timeout=300", "--websocket_connect_timeout=100", \
#     "chat_service.asgi:application", \
#     "-v", "3"]
