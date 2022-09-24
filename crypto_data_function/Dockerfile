FROM python:3.8.4-slim-buster

RUN apt update && apt upgrade -y && apt-get install -y libpq-dev python3-dev gcc && rm -rf /var/cache/apt && apt-get clean

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /srv

COPY main.py ./
COPY ../cloud_function/utils utils
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=$PYTHONPATH:/srv
EXPOSE 8080

CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app