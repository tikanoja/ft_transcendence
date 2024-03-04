#!/bin/bash

python manage.py makemigrations
python manage.py makemigrations user
python manage.py migrate

exec "$@"
