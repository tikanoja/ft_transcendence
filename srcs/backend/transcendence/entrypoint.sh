#!/bin/bash

python manage.py makemigrations
python manage.py makemigrations app
python manage.py migrate

exec "$@"
