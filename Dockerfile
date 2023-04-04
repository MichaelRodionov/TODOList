FROM python:3.11-slim

WORKDIR /todo_list_app

ENV PYTHONUNBUFFERED=1

COPY poetry.lock pyproject.toml ./
COPY core/. ./core
COPY todolist/. ./todolist
COPY manage.py .
COPY README.md .

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install
