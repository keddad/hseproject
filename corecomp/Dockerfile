FROM python:3.8.2-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./req.txt .

RUN pip install -r req.txt

COPY . .

CMD ["gunicorn", "main:app", "-w", "4", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker"]