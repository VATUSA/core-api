FROM python:3.10.5

EXPOSE 80

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install gitpython

RUN pip3 install --no-cache-dir -r /code/requirements.txt

COPY ./alembic.ini /code/alembic.ini

COPY ./dev /code/dev

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]