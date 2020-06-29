FROM python:3.8

RUN pip install poetry

COPY poetry.lock pyproject.toml ./

RUN poetry export -f requirements.txt -o requirements.txt

RUN pip install -r requirements.txt

COPY . ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3800"]