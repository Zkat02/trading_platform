#!/bin/sh
poetry run python -m celery --app trading_platform worker --loglevel=info
