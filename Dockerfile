FROM python:3.8.4-slim-buster

RUN apt update && apt-get install -y git && rm -rf /var/cache/apt && apt-get clean

COPY requirements.txt ./

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /srv

COPY .pylintrc ./
COPY orm orm
COPY scraper scraper
COPY tests tasts
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=$PYTHONPATH:/orm

CMD ["python3", "./orm/fixtures/twitter.py"]