FROM continuumio/miniconda3

WORKDIR /app

COPY environment.yaml .


RUN conda env create -f /app/environment.yaml
# Install mlflow and packages requied to interact with PostgreSQL and MinIO
RUN conda init bash
RUN echo "conda activate python3.7-env" > ~/.bashrc
COPY entrypoint.sh .
SHELL ["/bin/bash", "--login", "-c"]

ENV CORPORA omw-1.4 wordnet punkt stopwords

RUN python -m nltk.downloader $CORPORA;

RUN ls -la

ENTRYPOINT ["/app/entrypoint.sh"]

