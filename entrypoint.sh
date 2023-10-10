#!/bin/bash

#poetry shell
#poetry run django-admin
#poetry config virtualenvs.create false
#poetry install --no-root
poetry shell
poetry run python manage.py makemigrations
#poetry run python manage.py makemigrations user_management
poetry run python manage.py migrate
#
#poetry run python manage.py makemigrations admin
#poetry run python manage.py makemigrations auth


poetry run python manage.py runserver 0.0.0.0:8000
