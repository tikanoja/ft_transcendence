# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.2-slim-bookworm


# Set the working directory in the container
WORKDIR /

# Install openssl for SSL certificate generation
RUN apt-get update && \
    apt-get install -y openssl && \
    apt-get clean

RUN openssl req -newkey rsa:4096 -x509 -sha256 -days 10000 -nodes \
    -out /server.crt \
    -keyout /server.key \
    -subj "/C=FI/ST=Helsinki/L=Helsinki/O=42/OU=Hive/CN=pongchamps"

# Copy your application code into the container
COPY . .

RUN chmod +r /server.key
RUN chmod +r /server.crt

# Expose the port your application runs on
EXPOSE 8888

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Command to run your application
CMD [ "python3", "app.py" ]  # Replace app.py with your actual application file

#CMD ["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
