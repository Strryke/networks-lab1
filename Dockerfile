FROM python:3.11-buster

RUN pip install poetry

COPY . .

RUN poetry install

EXPOSE 8000
ENTRYPOINT ["poetry", "run", "uvicorn"]
CMD ["lab1.main:app", "--host", "0.0.0.0", "--port", "8000"]


