#!/bin/bash

set -e

while ! (timeout 3 bash -c "</dev/tcp/${DB_HOST}/${DB_PORT}") &> /dev/null;
do
    echo waiting for PostgreSQL to start...;
    sleep 3;
done;

#ping 8.8.8.8

./manage.py makemigrations --merge --no-input --traceback
./manage.py migrate --no-input --traceback
./manage.py collectstatic --no-input --traceback
./manage.py runserver 0.0.0.0:8000

sleep 5 && celery -A core beat -l info

sleep 5 && celery -A core worker -Q celery -l info
