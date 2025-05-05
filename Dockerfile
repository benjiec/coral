FROM python:3

RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y man

RUN python3 -m pip install lovis4u

RUN mkdir /coral
WORKDIR /coral
COPY . .
