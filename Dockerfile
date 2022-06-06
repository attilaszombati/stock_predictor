FROM python:3.8.4-slim-buster

RUN apt update && apt upgrade -y && apt-get install -y libpq-dev python3-dev gcc && rm -rf /var/cache/apt && apt-get clean

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /srv

COPY .pylintrc test.sh ./
COPY config config
COPY cloud_function/utils utils
COPY cloud_function/orm orm
COPY cloud_function/scraper scraper
COPY tests tests
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=$PYTHONPATH:/srv
EXPOSE 8080

CMD ["python3", "./scraper/twitter.py"]