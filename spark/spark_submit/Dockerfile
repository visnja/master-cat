FROM spark-base:latest

# RUN apk update && apk add build-base gcc g++ libffi-dev musl-dev python3-dev
COPY template.sh /
# COPY submit.sh /

ENV SPARK_MASTER_NAME spark-master
ENV SPARK_MASTER_PORT 7077


COPY spark_env.tar.gz /app/
