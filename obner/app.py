from locale import currency
from flask import Flask, request
import spacy_dbpedia_spotlight
import spacy
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
# load your model as usual
nlp = spacy.load('en_core_web_lg')
# add the pipeline stage
nlp.add_pipe('dbpedia_spotlight')

def runQuery(endpoint, prefix, q):
    ''' Run a SPARQL query with a declared prefix over a specified endpoint '''
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(prefix+q) # concatenate the strings representing the prefixes and the query
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def dict2df(results):
    ''' A function to flatten the SPARQL query results and return the column values '''
    if 'results' in results:
        data = []
        for result in results["results"]["bindings"]:
            tmp = {}
            for el in result:
                tmp[el] = result[el]['value']
            data.append(tmp)

        df = pd.DataFrame(data)
        return df
    else:
        print(results)
        return results['boolean']

def dfResults(endpoint, prefix, q):
    ''' Generate a data frame containing the results of running
        a SPARQL query with a declared prefix over a specified endpoint '''
    return dict2df(runQuery(endpoint, prefix, q))

def printQuery(results, limit=''):
    ''' Print the results from the SPARQL query '''
    if 'results' in results:
        resdata = results["results"]["bindings"]
        if limit != '':
            resdata = results["results"]["bindings"][:limit]
        for result in resdata:
            for ans in result:
                print('{0}: {1}'.format(ans, result[ans]['value']))
            print()
    else:
        print(results)

def printRunQuery(endpoint, prefix, q, limit=''):
    ''' Print the results from the SPARQL query '''
    results = runQuery(endpoint, prefix, q)
    printQuery(results, limit)

prefix = '''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbc: <http://dbpedia.org/resource/Category:>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    
    PREFIX ouseful:<http://ouseful.info/>
'''



#Declare the DBPedia endpoint
endpoint="http://dbpedia.org/sparql"
sparql = SPARQLWrapper(endpoint)



app = Flask(__name__)

label_dict = {
    "USD":"https://dbpedia.org/page/United_States_dollar",
    

}


def graph_search(entity,i=1):
    # page = entity.replace("http://dbpedia.org/resource/","")

    if i > 3:
        return False

    q ='''
    ASK {{

        <{page}> rdf:type dbo:Currency    
        
    }}
    '''.format(page=entity)
    isCurrency = dfResults(endpoint, prefix, q)

    if not isCurrency:
        q ='''
        SELECT ?o {{

                <{page}> dbo:wikiPageWikiLink ?o    
                
        }}
        '''.format(page=entity)
        df = dfResults(endpoint, prefix, q)
        if len(df)>0:
            df['currency'] = df.apply(lambda x: graph_search(x['o'],i+1), axis=1 )
        print(df.head())

    return isCurrency
    




@app.route("/ner", methods=["POST"])
def process():
    article = request.get_json()
    doc = nlp(article["text"])
    currencies = 0
    for ent in doc.ents:

        if graph_search(ent.kb_id_):
            currencies += 1

   
    res = {"status": currencies}
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
