FROM python:3

RUN pip install poetry

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN #poetry shell
RUN poetry install

COPY . /app/
