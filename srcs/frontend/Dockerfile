# base img
FROM alpine:3.18

# Install NGINX and SSL
RUN apk update && apk add --no-cache \
    nginx \
    openssl

# Ensure that we have the dir to store PID and SSL certs
RUN mkdir -p /run/nginx /etc/nginx/ssl /app/frontend

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

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Start NGINX
CMD ["nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"]
