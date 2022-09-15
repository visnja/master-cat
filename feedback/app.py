from flask import Flask, request, app
import json
import requests

from pymongo import MongoClient
import pandas as pd

connection=MongoClient("mongodb://mongodb:27017/feedback")

db=connection.get_database()

app = Flask(__name__)

def get_ner_probabilites(text):
    r = requests.post(url='http://obner:5000/ner',json={'text':text})
    print(r)
    return r

def get_model_predictions(text):
    r = requests.post(url='http://model_serve/invocations',json={'columns':["text"],'data':text})
    return r

def get_kb_labels(text):
    r = requests.post(url='http://knowledge-base:5000/label',json={'text':text})
    print(r)
    return r





@app.route("/feedback", methods=["POST"])
def process():
    article = request.get_json()
    print(article)
    text = article["text"]
    url =  article["url"]
    labels =  article["labels"]

    user_id = request.headers.get('X-User')

    probabilites = get_ner_probabilites(text).json().get('status')
    # predictions = get_model_predictions(text)
    kb_labels = get_kb_labels(text).json().get('status')

    penalty = 0

    for label in labels:
        if probabilites.get(label,0) < 0.5:
            print('Less likely to be the correct label if there are not enough entities connected to the label')
            penalty += 1
        # if label in predictions:
        #     continue
        if label not in kb_labels:
            print("Knowledge base doesn't recognize any tokens related to this label. Either the knowledge base is poor or this label is wrong")
            penalty += 0.5

    db.feedback.insert_one({'user_id':user_id,'penalty':penalty,'url':url,'text':text,'labels':labels})

    
        
    
   
    res = {"status": "ok"}
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
    