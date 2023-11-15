#!/bin/sh
poetry run python -m celery --app trading_platform beat --loglevel=info
