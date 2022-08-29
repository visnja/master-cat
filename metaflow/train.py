from metaflow import FlowSpec, step, IncludeFile, conda, conda_base
def get_python_version():
    """
    A convenience function to get the python version used to run this
    tutorial. This ensures that the conda environment is created with an
    available version of python.

    """
    import platform

    versions = {"2": "2.7.15", "3": "3.7.3"}
    return versions[platform.python_version_tuple()[0]]

def script_path(filename):
    """
    A convenience function to get the absolute path to a file in this
    tutorial's directory. This allows the tutorial to be launched from any
    directory.

    """
    import os

    filepath = os.path.join(os.path.dirname(__file__))
    return os.path.join(filepath, filename)

@conda_base(python=get_python_version(), libraries={"scikit-learn": "0.23.2"})
class TrainModelFlow(FlowSpec):

    """
    Train the model
    """
    @conda(libraries={"pymongo":"3.12.0","pandas":"1.3.4"})
    @step
    def start(self):
        import pandas as pd
        from pymongo import MongoClient
        connection=MongoClient("mongodb://localhost:27017/crawler.contents")

        db=connection.get_database()
        articles = pd.DataFrame(list(db.contents.find()))
        articles = articles.drop(columns=['visited','alternateImageUrl','created_at','contentType','date','icon','publishedAt','source','url'])
        articles = articles.sample(frac=1).reset_index(drop=True)
        self.classes = list(set(articles.classes_target.dropna().values.sum()))
        self.df = pd.concat([articles,articles['classes_target'].fillna("").map(lambda x: ",".join(x)).str.get_dummies(sep=",")],axis=1)
        self.next(self.a)   

    @conda(libraries={"pandas":"1.3.4","bson":"0.5.9","regex":"2022.3.15","nltk":"3.7"})
    @step
    def a(self):
        import os
        os.system('pip install contractions')
        import classification
        to_remove = ['ARS','MXN','OIL','XAU','TRY','INDEX','BTC','TWD','RUB','CHF']
        self.df = self.df.drop(labels=to_remove,axis=1)
        self.classes = [cls for cls in self.classes if cls not in to_remove]
        self.df['text_clean'] = self.df.body.map(lambda x: " ".join(list(x)) if type(x) is list else "" ).map(lambda com : classification.clean_text(com))
        self.next(self.b)
    
    @conda(libraries={"pandas":"1.3.4","bson":"0.5.9","regex":"2022.3.15","nltk":"3.7"})
    @step
    def b(self):
        from classification import BinaryRelevanceClassifier, accuracy_score, stop_words
        from sklearn.model_selection import train_test_split, GridSearchCV
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics import make_scorer
        # self.df = self.df.sample(4000)
        train, test = train_test_split(self.df[(self.df[self.classes].sum(axis=1)>0)], random_state=42, test_size=0.50, shuffle=True)
        X_train = train.text_clean
        y_train = train[self.classes]
        y_test = train[self.classes]
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
# fit
        br_clf.fit(vectorizer.transform(X_train).toarray(), y_train)
        print(br_clf.best_params_)
        print(br_clf.best_score_)
        best = BinaryRelevanceClassifier(br_clf.best_params_['base_classifier'])
        best.fit(vectorizer.transform(X_train).toarray(), y_train)
        y_pred = best.predict(vectorizer.transform(X_test).toarray())
        self.result = accuracy_score(y_test, y_pred)
        self.next(self.end)

    @step
    def end(self):
        """
        End the flow.

        """
        pass

    

if __name__ == "__main__":
    TrainModelFlow()
