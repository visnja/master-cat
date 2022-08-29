import os
import tempfile
from pprint import pprint

import pandas as pd
from pymongo import MongoClient
import utils
from utils import BinaryRelevanceClassifier, accuracy_score, stop_words
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import make_scorer

import mlflow
from mlflow.tracking import MlflowClient


def save_text(path, text):
    with open(path, "w") as f:
        f.write(text)


#  NOTE: ensure the tracking server has been started with --serve-artifacts to enable
#        MLflow artifact serving functionality.

def fetch_articles():
    connection = MongoClient("mongodb://mongodb:27017/crawler.contents")

    db = connection.get_database()
    articles = pd.DataFrame(list(db.contents.find()))
    articles = articles.drop(columns=['visited','alternateImageUrl','created_at','contentType','date','icon','publishedAt','source','url'])
    articles = articles.sample(frac=1).reset_index(drop=True)
    classes = list(set(articles.classes_target.dropna().values.sum()))
    df = pd.concat([articles,articles['classes_target'].fillna("").map(lambda x: ",".join(x)).str.get_dummies(sep=",")],axis=1)
    return df, classes

def filter_classes(df,classes, to_remove= ['ARS','MXN','OIL','XAU','TRY','INDEX','BTC','TWD','RUB','CHF']):
    df = df.drop(labels=to_remove,axis=1)
    classes = [cls for cls in classes if cls not in to_remove]
    return df, classes

def clean_text(df):
    df['text_clean'] = df.body.map(lambda x: " ".join(list(x)) if type(x) is list else "" ).map(lambda com : utils.clean_text(com))
    return df

def log_artifacts():
    # Upload artifacts
    with mlflow.start_run() as run, tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path_a = os.path.join(tmp_dir, "a.txt")
        save_text(tmp_path_a, "0")
        tmp_sub_dir = os.path.join(tmp_dir, "dir")
        os.makedirs(tmp_sub_dir)
        tmp_path_b = os.path.join(tmp_sub_dir, "b.txt")
        save_text(tmp_path_b, "1")
        mlflow.log_artifact(tmp_path_a)
        mlflow.log_artifacts(tmp_sub_dir, artifact_path="dir")
        return run.info.run_id

def train(df,classes):
    train, test = train_test_split(df[(df[classes].sum(axis=1)>0)], random_state=42, test_size=0.50, shuffle=True)
    X_train = train.text_clean
    y_train = train[classes]
    y_test = test[classes]
    X_test = test.text_clean
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    vectorizer.fit(train.text_clean)
    parameters = [
        {
            'base_classifier':[DecisionTreeClassifier(min_samples_leaf=2)],
            'base_classifier__criterion':['gini','entropy','log_loss'],
            'base_classifier__max_depth':[5,10,15,20]
        }
    ]

    br_clf = GridSearchCV(BinaryRelevanceClassifier(),parameters, scoring=make_scorer(accuracy_score),verbose=2, cv=5)    
    br_clf.fit(vectorizer.transform(X_train).toarray(), y_train)
    print(br_clf.best_params_)
    print(br_clf.best_score_)
    best = BinaryRelevanceClassifier(br_clf.best_params_['base_classifier'])
    best.fit(vectorizer.transform(X_train).toarray(), y_train)
    y_pred = best.predict(vectorizer.transform(X_test).toarray())
    result = accuracy_score(y_test, y_pred)
    return best

def main():
    df, classes = fetch_articles()
    df, classes = filter_classes(df, classes)
    df = clean_text(df)
    df = df.sample(4000)
    best = train(df, classes)
    mlflow.sklearn.log_model(best, "model")
    print("Model saved in run %s" % mlflow.active_run().info.run_uuid)
    # assert "MLFLOW_TRACKING_URI" in os.environ

    # # Log artifacts
    # run_id1 = log_artifacts()
    # # Download artifacts
    # client = MlflowClient()
    # print("Downloading artifacts")
    # pprint(os.listdir(client.download_artifacts(run_id1, "")))
    # pprint(os.listdir(client.download_artifacts(run_id1, "dir")))

    # # List artifacts
    # print("Listing artifacts")
    # pprint(client.list_artifacts(run_id1))
    # pprint(client.list_artifacts(run_id1, "dir"))

    # # Log artifacts again
    # run_id2 = log_artifacts()
    # # Delete the run to test `mlflow gc` command
    # client.delete_run(run_id2)
    # print(f"Deleted run: {run_id2}")


if __name__ == "__main__":
    main()
