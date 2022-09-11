from flask import Flask, request
import spacy_dbpedia_spotlight
import spacy
import json
# load your model as usual
nlp = spacy.load('en_core_web_lg')
# add the pipeline stage
nlp.add_pipe('dbpedia_spotlight')


app = Flask(__name__)

label_dict = {
    "USD":"",
    

}

def graph_search(entity):
    pass




@app.route("/ner", methods=["POST"])
def process():
    article = request.get_json()
    print(article)
    doc = nlp(article["text"])
    print(article)
    print('Entities', [(ent.text, ent.label_, ent.kb_id_) for ent in doc.ents])
   
    res = {"status": "ok"}
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
