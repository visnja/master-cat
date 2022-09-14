
from flask import Flask, request
import spacy
import pickle
import json
app = Flask(__name__)
nlp = spacy.load('en_core_web_lg')


with open('matcherpickle.pkl','rb') as fi:
    matcher = pickle.load(fi)


@app.route("/label", methods=["POST"])
def label():
    text = request.get_json()["text"]
    classes = []
    tokens = nlp(text)
    matches = matcher(tokens)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        classes.append(string_id)
        span = tokens[start:end]  # The matched span

    res = {"status": list(set(classes))}
    return json.dumps(res)



if __name__ == '__main__':
    app.run(debug=True)