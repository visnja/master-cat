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
        print()

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
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX dbc: <http://dbpedia.org/resource/Category:>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    
    PREFIX ouseful:<http://ouseful.info/>
'''



#Declare the DBPedia endpoint
endpoint="http://dbpedia.org/sparql"
sparql = SPARQLWrapper(endpoint)



app = Flask(__name__)



def direct_children(entity):
    q ='''
        SELECT ?code {{

            <{page}> dbo:wikiPageWikiLink ?o .
            ?o rdf:type dbo:Currency .
            ?o dbp:isoCode ?code .
                
        }}
        '''.format(page=entity)
    df = dfResults(endpoint, prefix, q)
    return df

def children_with_grandchildren(entity):
    q ='''
        SELECT ?code, COUNT(?code) as ?count {{

            <{page}> dbo:wikiPageWikiLink ?child .
            ?child dbo:wikiPageWikiLink ?grandchild .
            ?grandchild rdf:type dbo:Currency .
            ?grandchild dbp:isoCode ?code .
            FILTER NOT EXISTS {{ ?child rdf:type dbo:Currency . }}
                
        }} GROUP BY ?code
        '''.format(page=entity)
    df = dfResults(endpoint, prefix, q)
    return df

def graph_search(entity):
    labels = {}

    q ='''
    ASK {{

        <{page}> rdf:type dbo:Currency    
        
    }}
    '''.format(page=entity)
    isCurrency = dfResults(endpoint, prefix, q)
    if isCurrency:
        q ='''
        SELECT ?code {{

            <{page}> dbp:isoCode ?code .   
            
        }}
        '''.format(page=entity)
        code = dfResults(endpoint, prefix, q)
        labels[code['code'][0]] = 100


    if not isCurrency:
        children = direct_children(entity)
        grandchildren = children_with_grandchildren(entity)
        for idx,child in children.iterrows():
            labels[child['code']] = 50
        for idx,child in grandchildren.iterrows():
            labels[child['code']] = child['count']

        

    return labels



@app.route("/ner", methods=["POST"])
def process():
    article = request.get_json()
    doc = nlp(article["text"])
    currencies = {}
    for ent in doc.ents:

        labels = graph_search(ent.kb_id_)
        for key, value in labels.items():
            if key in currencies:
                currencies[key] += int(value)
            else:
                currencies[key] = int(value)

   
    res = {"status": currencies}
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
