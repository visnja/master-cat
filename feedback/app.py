from flask import Flask, request, app
import json
import requests

from pymongo import MongoClient
import pandas as pd

connection=MongoClient("mongodb://mongodb:27017/feedback")

db=connection.get_database()

app = Flask(__name__)

def get_ner_probabilites(text):
    r = requests.post(url='http://obner/ner',json={'text':text})
    return r['labels']

def get_model_predictions(text):
    r = requests.post(url='http://model_serve/invocations',json={'columns':["text"],'data':text})
    return r

def get_kb_labels(text):
    r = requests.post(url='http://knowledge_base/label',json={'text':text})
    return r


@app.route("/feedback", methods=["POST"])
def process():
    article = request.get_json()
    print(article)
    text = article["text"]
    url =  article["url"]
    labels =  article["labels"]

    probabilites = get_ner_probabilites(text)
    predictions = get_model_predictions(text)
    kb_labels = get_kb_labels(text)

    penalty = 0

    for label in labels:
        if probabilites[label] < 0.5:
            print('Less likely to be the correct label if there are not enough entities connected to the label')
            penalty += 1
        if label in predictions:
            continue
        if label not in kb_labels:
            print("Knowledge base doesn't recognize any tokens related to this label. Either the knowledge base is poor or this label is wrong")
            penalty += 0.5

    
        
    
   
    res = {"status": "ok"}
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
    