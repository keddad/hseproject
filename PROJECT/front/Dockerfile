FROM python:3.8

RUN pip3 install pipenv

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN apt-get update && apt-get install cmake -y

RUN pipenv install --deploy --system

RUN apt-get clean

COPY . .

CMD ["python", "main.py"]