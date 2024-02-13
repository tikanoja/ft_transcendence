#!/bin/sh

while ! nc -z backend 8000; do
	echo "Waiting for backend service..."
	sleep  1
done
echo "Starting NGINX !"

exec "$@"
