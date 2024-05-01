FROM python:3.10-slim

WORKDIR /pto-calculator

RUN apt-get update -y && \
     apt-get install -y python3-pip && \
     apt-get install -y postgresql && \
     apt-get -y install libpq-dev gcc

RUN pip3 install --upgrade pip && \
    pip3 install --upgrade wheel && \
    pip3 install --upgrade setuptools && \
    pip3 install psycopg2

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/pto-calculator"

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]