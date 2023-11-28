#!/bin/bash

poetry run python manage.py makemigrations user_management
poetry run python manage.py migrate user_management

poetry run python manage.py makemigrations
poetry run python manage.py migrate

poetry run python manage.py runserver 0.0.0.0:8000
