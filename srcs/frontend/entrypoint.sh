#!/bin/sh

while ! nc -z pong_service 8000; do
	echo "Waiting for pong_service service..."
	sleep  1
done
echo "Starting NGINX !"

exec "$@"
