#!/bin/bash

set -e

whoami

python manage.py wait_for_db
# python manage.py collectstatic --noinput

python manage.py migrate
# python manage.py fixtree
gunicorn newspaper_headline_creator.wsgi:application --bind 0.0.0.0:8000

