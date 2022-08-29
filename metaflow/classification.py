
from sklearn.base import BaseEstimator, ClassifierMixin, clone
import random
from sklearn.linear_model import LogisticRegression
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted

import re
import nltk
import contractions
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
import pandas as pd

class ClassifierChains(BaseEstimator, ClassifierMixin):
    def __init__(
        self,
        base_classifier=LogisticRegression(max_iter=20000),
        order=None,
        classes=None,
    ):
        self.base_classifier = base_classifier
        self.order = order
        self.classes = classes

    def fit(self, X, y):
        """
        Build a Classifier Chain from the training set (X, y).
        Parameters
        ----------
        X : array-like or sparse matrix, shape = [n_samples, n_features]
            The training input samples. Internally, it will be converted to
            ``dtype=np.float32`` and if a sparse matrix is provided
            to a sparse ``csc_matrix``.
        y : array-like, shape = [n_samples, n_labels]
            The target values (class labels) as integers or strings.

        """

        # check the order parameter
        if self.order is None:
            # default value - natural order for number of labels
            self.order = list(range(y.shape[1]))
        elif self.order == "random":
            # random order
            self.order = list(range(y.shape[1]))
            random.shuffle(self.order)
        else:
            # order specified
            if len(self.order) == y.shape[1]:
                # expect order from 1, hence reduce 1 to consider zero indexing
                self.order = [o - 1 for o in self.order]

        # list of base models for each class
        self.models = [clone(self.base_classifier) for clf in range(y.shape[1])]

        # create a copy of X
        X_joined = X.copy()
        # X_joined.reset_index(drop=True, inplace=True)

        # create a new dataframe with X and y-in the order specified
        # if order = [2,4,5,6...] -> X_joined= X, y2, y4, y5...
        for val in self.order:
            X_joined = pd.concat([X_joined, y[self.classes[val]]], axis=1)

        # for each ith model, fit the model on X + y0 to yi-1 (in the order specified)
        # if order = [2,4,6,....] fit 1st model on X for y2, fit second model on X+y2 for y4...
        for chain_index, model in enumerate(self.models):
            # select values of the class in order
            y_vals = y.loc[:, self.classes[self.order[chain_index]]]
            # pick values for training - X+y upto the current label
            t_X = X_joined.iloc[:, : (X.shape[1] + chain_index)]
            check_X_y(t_X, y_vals)
            # fit the model
            model.fit(t_X, y_vals)

    # The predict function to make a set of predictions for a set of query instances
    def predict(self, X):

        # check if the models list has been set up
        check_is_fitted(self, ["models"])

        # dataframe to maintain previous predictions
        pred_chain = pd.DataFrame(columns=[self.classes[o] for o in self.order])

        X_copy = X.copy()
        X_joined = X.copy()

        # use default indexing
        X_joined.reset_index(drop=True, inplace=True)
        X_copy.reset_index(drop=True, inplace=True)

        i = 0

        # for each ith model, predict based on X + predictions of all models upto i-1
        # happens in the specified order since models are already fitted according to the order
        for chain_index, model in enumerate(self.models):
            # select previous predictions - all columns upto the current index
            prev_preds = pred_chain.iloc[:, :chain_index]
            # join the previous predictions with X
            X_joined = pd.concat([X_copy, prev_preds], axis=1)
            # predict on the base model
            pred = model.predict(X_joined)
            # add the new prediction to the pred chain
            pred_chain[self.classes[self.order[i]]] = pred
            i += 1

        # re-arrange the columns in natural order to return the predictions
        pred_chain = pred_chain.loc[
            :, [self.classes[j] for j in range(0, len(self.order))]
        ]
        # all sklearn implementations return numpy array
        # hence convert the dataframe to numpy array
        return pred_chain.to_numpy()

    # Function to predict probabilities of 1s
    def predict_proba(self, X):
        # check if the models list has been set up
        check_is_fitted(self, ["models"])

        # dataframe to maintain previous predictions
        pred_chain = pd.DataFrame(columns=[self.classes[o] for o in self.order])
        # dataframe to maintain probabilities of class labels
        pred_probs = pd.DataFrame(columns=[self.classes[o] for o in self.order])
        X_copy = X.copy()
        X_joined = X.copy()

        # use default indexing
        X_joined.reset_index(drop=True, inplace=True)
        X_copy.reset_index(drop=True, inplace=True)

        i = 0

        # for each ith model, predict based on X + predictions of all models upto i-1
        # happens in the specified order since models are already fitted according to the order
        for chain_index, model in enumerate(self.models):

            # select previous predictions - all columns upto the current index
            prev_preds = pred_chain.iloc[:, :chain_index]
            # join the previous predictions with X
            X_joined = pd.concat([X_copy, prev_preds], axis=1)
            # predict on the base model
            pred = model.predict(X_joined)
            # predict probabilities
            pred_proba = model.predict_proba(X_joined)
            # add the new prediction to the pred chain
            pred_chain[self.classes[self.order[i]]] = pred
            # save the probabilities of 1 according to label order
            pred_probs[self.classes[self.order[i]]] = [
                one_prob[1] for one_prob in pred_proba
            ]
            i += 1

        # re-arrange the columns in natural order to return the probabilities
        pred_probs = pred_probs.loc[
            :, [self.classes[j] for j in range(0, len(self.order))]
        ]
        # all sklearn implementations return numpy array
        # hence convert the dataframe to numpy array
        return pred_probs.to_numpy()


class BinaryRelevanceClassifierUS(BaseEstimator, ClassifierMixin):
    def __init__(self, base_classifier=LogisticRegression(max_iter=20000)):
        self.base_classifier = base_classifier

    def fit(self, X, y):
        """Build a Binary Relevance classifier with Under sampling from the training set (X, y).
        Parameters
        ----------
        X : array-like or sparse matrix, shape = [n_samples, n_features]
            The training input samples. Internally, it will be converted to
            ``dtype=np.float32`` and if a sparse matrix is provided
            to a sparse ``csc_matrix``.
        y : array-like, shape = [n_samples]
            The target values (class labels) as integers or strings.
        """

        # list of individual classifiers
        self.models = []

        # for each class label
        for label in list(y.columns):

            X_cp = X.copy()
            # pick the column values for the label
            y_cp = y[label]

            # sampling is done on both X and y, hence join the two dataframes
            X_y_data = pd.concat([X_cp, y_cp], axis=1)

            # counters for 0 values and 1 values
            n_val0, n_val1 = 0, 0

            j = 0
            # for each sample
            while j < len(X_y_data):
                # if value for the label is 0
                if X_y_data.iloc[j][label] == 0:
                    n_val0 += 1
                else:
                    # value 1
                    n_val1 += 1
                j += 1

            # under sample the majority class
            # randomly pick samples from majority class equal to the number of samples in the minority class
            # both the classes will have the same number of samples
            if n_val0 > n_val1:
                # majority 0 values
                val1 = X_y_data[X_y_data[label] == 1]
                val0 = X_y_data[X_y_data[label] == 0].sample(n_val1)

                X_y_data = pd.concat([val0, val1], axis=0)

            elif n_val1 > n_val0:
                # majority 1 values
                val1 = X_y_data[X_y_data[label] == 1].sample(n_val0)
                val0 = X_y_data[X_y_data[label] == 0]

                X_y_data = pd.concat([val0, val1], axis=0)

            # split back into X and y
            X_cp = X_y_data.iloc[:, :-1]
            y_cp = X_y_data.iloc[:, -1]

            base_model = clone(self.base_classifier)
            # fit the base model - one model each for Y1, Y2....Y14
            a, b = check_X_y(X_cp, y_cp)
            base_model.fit(a, b)
            # list of individual classifiers classifiers
            self.models.append(base_model)

    # The predict function to make a set of predictions for a set of query instances
    def predict(self, X):
        # check if the models list has been set up
        check_is_fitted(self, ["models"])
        X = check_array(X)

        all_preds = pd.DataFrame()
        i = 0
        # list of individual classifier predictions
        preds = []

        # for every fitted model
        for model in self.models:
            # predict for X
            pred = model.predict(X)
            # add to the list of predictions
            preds.append(pd.DataFrame({"Class" + str(i + 1): pred}))
            i += 1

        # store predictions for each label in a single dataframe
        all_preds = pd.concat(preds, axis=1)
        # standard sklearn classifiers return predictions as numpy arrays
        # hence convert the dataframe to a numpy array
        return all_preds.to_numpy()

    def predict_proba(self, X):
        # check if the models list has been set up
        check_is_fitted(self, ["models"])
        X = check_array(X)

        all_preds = pd.DataFrame()
        i = 0

        for model in self.models:
            # Call predict_proba of the each base model
            pred = model.predict_proba(X)
            # Add the probabilities of 1 to the dataframe
            all_preds["Class" + str(i + 1)] = [one_prob[1] for one_prob in pred]
            i += 1

        # return probabilities
        return all_preds.to_numpy()


class BinaryRelevanceClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, base_classifier=LogisticRegression()):
        self.base_classifier = base_classifier

    def fit(self, X, y):
        """Build a Binary Relevance classifier from the training set (X, y).
        Parameters
        ----------
        X : array-like or sparse matrix, shape = [n_samples, n_features]
            The training input samples. Internally, it will be converted to
            ``dtype=np.float32`` and if a sparse matrix is provided
            to a sparse ``csc_matrix``.
        y : array-like, shape = [n_samples, n_labels]
            The target values (class labels) as integers or strings.
        """

        # list of individual classifiers
        self.models = []

        # for every class label
        for label in list(y.columns):
            # Check that X and y have correct shape
            x_checked, y_checked = check_X_y(X, y[label])
            # every classifier is independent of the others
            # hence we create a copy of the base classifier instance
            base_model = clone(self.base_classifier)
            # fit the base model - one model each for Y1, Y2....Y14
            basel_model = base_model.fit(x_checked, y_checked)
            # add the fitted model list of individual classifiers
            self.models.append(base_model)

    # The predict function to make a set of predictions for a set of query instances
    def predict(self, X):
        # check if the models list has been set up
        check_is_fitted(self, ["models"])
        X = check_array(X)

        all_preds = pd.DataFrame()
        i = 0
        # list of individual classifier predictions
        preds = []

        # predict against each fitted model - one model per label
        for model in self.models:
            pred = model.predict(X)
            # add the prediction to the dataframe
            preds.append(pd.DataFrame({"Class" + str(i + 1): pred}))
            i += 1

        # dataframe with predictions for all class labels
        all_preds = pd.concat(preds, axis=1)
        # standard sklearn classifiers return predictions as numpy arrays
        # hence convert the dataframe to a numpy array
        return all_preds.to_numpy()

    def predict_proba(self, X):
        # check if the models list has been set up
        check_is_fitted(self, ["models"])
        X = check_array(X)

        all_preds = pd.DataFrame()
        i = 0

        for model in self.models:
            # Call predict_proba of the each base model
            pred = model.predict_proba(X)
            # Add the probabilities of 1 to the dataframe
            all_preds["Class" + str(i + 1)] = [one_prob[1] for one_prob in pred]
            i += 1

        # return probabilities
        return all_preds.to_numpy()
def accuracy_score(y_test, y_pred):
    # y_pred is a numpy array, y_test is a dataframe
    # to compare the two, convert to a single type
    y_test = y_test.to_numpy()
    
    # shape of test and preds must be equal
    assert y_test.shape == y_pred.shape
    i=0
    # list of scores for each training sample
    scores = []
    
    # for each test sample
    while i < len(y_test):
        count=0
        # count the number of matches in the sample
        # y_test[i] -> row values in test set (true values)
        # y_pred[i] -> row values in predictions set (predicted values)
        for p, q in zip(y_test[i], y_pred[i]):
            if p == q:
                count += 1

        # accuracy score for the sample = no. of correctly predicted labels/total no. of labels
        scores.append(count / y_pred.shape[1])
        i+=1 

    # final accuracy = avg. accuracy over all test samples =
    # sum of the accuracy of all training samples/no. of training samples
    return round((sum(scores)/len(y_test)), 5)

def clean_text(txt):
        

    txt = re.sub(r'\d+ min read', '', str(txt), flags=re.IGNORECASE)
    txt = re.sub(r'by reuters staff', '', str(txt), flags=re.IGNORECASE)
    ### separate sentences with '. '
    txt = re.sub(r'\.(?=[^ \W\d])', '. ', str(txt))
    ### remove punctuations and characters
    txt = re.sub(r'[^\w\s]', '', txt) 
    ### strip
    txt = " ".join([word.strip() for word in txt.split()])
    ### lowercase
    txt = txt.lower() 
    ### slang
    txt = contractions.fix(txt) 
    ### tokenize (convert from string to list)
    lst_txt = txt.split()
    ### stemming (remove -ing, -ly, ...)
    
    ps = nltk.stem.porter.PorterStemmer()
    lst_txt = [ps.stem(word) for word in lst_txt]
    ### lemmatization (convert the word into root word)
    
    lem = nltk.stem.wordnet.WordNetLemmatizer()
    lst_txt = [lem.lemmatize(word) for word in lst_txt]
    
    lst_txt = [word for word in lst_txt if word not in 
            stop_words]
    ### back to string
    txt = " ".join(lst_txt)
    return txt
