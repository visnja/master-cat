FROM spark-submit:latest

RUN apt update && apt install dumb-init

COPY requirements.txt /app/
RUN cd /app \
      && pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt


COPY submit.sh /submit.sh

COPY main.py /app/app.py

ENV SPARK_APPLICATION_PYTHON_LOCATION /app/app.py
ENTRYPOINT [ "dumb-init", "--" ]
CMD ["/bin/bash", "/template.sh"]