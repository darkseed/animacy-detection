import sys

import seaborn as sb
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import LabelEncoder

from gensim.models.word2vec import Word2Vec

from experiment import FeatureStacker, WordEmbeddings, Windower, load_data
from experiment import include_features


model = Word2Vec.load(sys.argv[1])
X, y = load_data(sys.argv[2])

X_train_idx, X_test_idx, y_train_idx, y_test_idx = train_test_split(
    range(len(X)), range(len(X)), test_size=0.2, random_state=2014)
X_train_docs = [X[i] for i in X_train_idx]
y_train_docs = [label for i in y_train_idx for label in y[i]]
X_test_docs = [X[i] for i in X_test_idx]
y_test_docs = [label for i in y_test_idx for label in y[i]]

scores = np.zeros((10, 3))
sizes = []
for i, train_size in enumerate(np.arange(0.1, 1.1, 0.1)):
    size = int(len(X_train_docs) * train_size)
    sizes.append(size)
    X_train = include_features(X_train_docs[:size], ('word', 'pos'))
    X_test = include_features(X_test_docs, ('word', 'pos'))
    features = FeatureStacker(('windower', Windower(window_size=3)),
                              ('embeddings', WordEmbeddings(model)))
    X_train = features.fit_transform(X_train)
    X_test = features.transform(X_test)
    le = LabelEncoder()
    y_train = le.fit_transform(y_train_docs[:X_train.shape[0]])
    y_test = le.transform(y_test_docs)
    clf = LogisticRegression(C=1.0)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    scores[i] = precision_recall_fscore_support(y_test, preds, average='micro')[:3]

df = pd.DataFrame(scores, index=sizes, columns=['precision', 'recall', 'F-score'])
df.plot()
sb.plt.savefig("learning_curve.pdf")