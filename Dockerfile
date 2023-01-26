FROM python:3.10

WORKDIR /auth-server

COPY ./requirements.txt /auth-server/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /auth-server/requirements.txt

COPY ./src /auth-server/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]