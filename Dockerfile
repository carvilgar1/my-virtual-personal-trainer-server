# syntax=docker/dockerfile:1
FROM python:3.10.8-alpine
WORKDIR /my_virtual_personal_trainer
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_APP=appcore/interfaces/app.py
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY ./src .
CMD ["flask", "run"]