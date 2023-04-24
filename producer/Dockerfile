FROM python:3.7-slim

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENV KAFKA_BROKER="kafka:9092"
ENV SUBREDDIT="forex"

CMD ["python", "-u", "./main.py"]