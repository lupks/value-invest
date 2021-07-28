# syntax=docker/dockerfile:1

FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN . venv/bin/activate

COPY main.py .
CMD ["python3", "main.py"]