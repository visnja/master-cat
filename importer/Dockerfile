FROM ubuntu:bionic

RUN apt-get upgrade && apt-get update && DEBIAN_FRONTENT=noninteractive apt-get -y install default-jre-headless python3 python3-pip && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENV MONGO_URL "mongodb://mongodb:27017/crawler.contents"
COPY main.py .

CMD ["python3","main.py"]