FROM python:3.11-slim

RUN mkdir /walk-profile

WORKDIR /walk-profile

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /walk-profile/docker/*.sh
