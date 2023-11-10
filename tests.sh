#!/bin/sh
docker exec -it trading_platform-web-1 bash
# poetry run python run_all_tests.py
poetry run python manage.py test
