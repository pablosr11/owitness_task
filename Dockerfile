FROM python:slim-buster
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
# only for demo purposes - api can be run as-is
COPY ./orbital.db /code/orbital.db 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]