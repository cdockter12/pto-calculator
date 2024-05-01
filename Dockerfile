FROM python:3.10.18-slim

WORKDIR /pto-calculator

RUN apt-get update -y && apt-get install -y \
     python3-pip \
     postgresql

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/pto-calculator"

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]