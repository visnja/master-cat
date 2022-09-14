FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt && python3 -m spacy download en_core_web_lg

COPY . .

CMD ["python3","-m","flask","run","--host=0.0.0.0"]