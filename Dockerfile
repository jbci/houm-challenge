FROM python:3.9-bullseye
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update

RUN apt install -y python3.9-dev
RUN apt install -y python3.9-venv
RUN apt install -y python3-pip
RUN apt install -y gdal-bin
RUN apt install -y sqlite3
RUN apt install -y spatialite-bin
RUN apt install -y git
RUN apt install -y proj-bin
RUN apt install -y libsqlite3-mod-spatialite


RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./houm_challenge .

# COPY ./run_script.sh .
# CMD ["sh run_script.sh"]