FROM spark-base:latest


COPY template.sh /


ENV SPARK_MASTER_NAME spark-master
ENV SPARK_MASTER_PORT 7077
# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt /app/
RUN cd /app \
      && pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Copy the source code


COPY spark_env.tar.gz /app/

COPY newsubmit.sh /submit.sh

COPY main.py /app/app.py

ENV SPARK_APPLICATION_PYTHON_LOCATION /app/app.py
CMD ["/bin/bash", "/template.sh"]