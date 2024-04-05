# base img
FROM alpine:3.18

# Install NGINX and SSL
RUN apk update && apk add --no-cache \
    nginx \
    openssl \
	python3 \
	py3-pip \
	certbot \
	python3-certbot-nginx

# Ensure that we have the dir to store PID and SSL certs
RUN mkdir -p /run/nginx /etc/nginx/ssl /app/frontend

RUN certbot --nginx -d example.com -d www.example.com
# Generate SSL cert & key
RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
    -out /etc/nginx/ssl/certificate.crt \
    -keyout /etc/nginx/ssl/certificate.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

# Add a new user within the container
RUN adduser -D -H -s /sbin/nologin -g www-data -G www-data www-data

# Copy NGINX configuration to the container
COPY conf/nginx.conf /etc/nginx/nginx.conf
RUN chmod 644 /etc/nginx/nginx.conf

# RUN openssl req -new -x509 -key ca-key.pem -out ca-cert.pem -days 365

COPY ./client.py /client.py
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir websockets

# Copy requirements.txt into the image
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

RUN apk add --no-cache curl \
    && curl -o socket.io.min.js https://cdn.socket.io/4.3.1/socket.io.min.js \
    && apk del curl

ENTRYPOINT ["/entrypoint.sh"]

# Start NGINX
CMD ["nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]
