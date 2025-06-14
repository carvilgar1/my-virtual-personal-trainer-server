FROM python:3.12.8-bullseye

ARG HTTP_PORT

ENV PYTHONPATH=/server
ENV FLASK_APP=src.app.py

WORKDIR /server

COPY requirements.txt /server
COPY src/ /server/src

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

EXPOSE ${HTTP_PORT}

CMD ["flask", "run", "--host=0.0.0.0"]