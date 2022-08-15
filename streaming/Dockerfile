FROM ubuntu:bionic

RUN apt-get upgrade && apt-get update && \
 DEBIAN_FRONTENT=noninteractive apt-get -y install wget make default-jre-headless zlib1g-dev gcc libssl-dev bzip2 libffi-dev && apt-get clean && \
 rm -rf /var/lib/apt/lists/*
RUN wget https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz && \
 mv Python-3.7.12.tgz /opt/ && cd /opt/ && tar xzf Python-3.7.12.tgz && \
 rm -f /opt/Python-3.7.12.tgz && cd Python-3.7.12 && \
  ./configure --enable-optimisations && make install

RUN python3.7 -V
RUN ln -s /usr/local/bin/python3.7 /usr/bin/python3
RUN ln -s /usr/local/bin/pip3.7 /usr/bin/pip3
COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENV MONGO_URL "mongodb://mongodb:27017/crawler.contents"
ENV PYSPARK_PYTHON python3

COPY *.py ./

CMD ["python3","main.py"]