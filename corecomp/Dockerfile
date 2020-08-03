FROM python:3.8

ENV WEB_CONCURRENCY 4

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN apt-get update && apt-get install cmake -y

RUN pipenv install --system

RUN apt-get clean

COPY . ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3800", "--ws", "none", "--proxy-headers"]
