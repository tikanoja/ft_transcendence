# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.2-slim-bookworm


# Set the working directory in the container
WORKDIR /

# Install openssl for SSL certificate generation
RUN apt-get update && \
    apt-get install -y openssl && \
    apt-get clean

# Copy SSL certificates into the container
#COPY ./ssl_certs/server.crt /etc/ssl/certs/server.crt
#COPY ./ssl_certs/server.key /etc/ssl/private/server.key
#COPY ./ssl_certs/ca.crt /etc/ssl/certs/ca.crt

# Generate SSL certificates if they don't exist
RUN openssl req -newkey rsa:2048 -x509 -sha256 -days 365 -nodes \
    -out /server.crt \
    -keyout /server.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"


#RUN openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/server.key -out /etc/ssl/certs/server.crt -days 10000 -nodes -subj "/CN=localhost"

# Copy your application code into the container
COPY . .

RUN chmod +rwx /server.key
RUN chmod +rwx /server.crt

# Set up any environment variables if necessary
# For example, setting environment variables for SSL
#ENV SSL_CERT_FILE=/server.crt
#ENV SSL_KEY_FILE=/server.key
ENV PYTHONASYNCIODEBUG=1
#ENV SSL_CA_FILE=/etc/ssl/certs/ca.crt

# Expose the port your application runs on
EXPOSE 8888

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Command to run your application
CMD [ "python3", "app.py" ]  # Replace app.py with your actual application file

#CMD ["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
