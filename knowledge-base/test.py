import spacy
import pickle


nlp = spacy.load('en_core_web_lg')


with open('matcherpickle.pkl','rb') as fi:
    matcher = pickle.load(fi)
    
text = 'the euro has fallen'


classes = []
tokens = nlp(text)
matches = matcher(tokens)
for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]  # Get string representation
    classes.append(string_id)
    span = tokens[start:end]  # The matched span
print(list(set(classes)))
