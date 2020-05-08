FROM python:3.8.2-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY . .

CMD ["gunicorn", "main:app", "-w", "4", "-b", "0.0.0.0:3800", "-k", "uvicorn.workers.UvicornWorker"]