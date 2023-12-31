# -*- coding: utf-8 -*-
"""KS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PPm47QJywRkD9ouwBRTmSjPEoqi9dWtI

## Generate similar (Gensim)

Gensim is an open source Python library for representing documents as semantic vectors. <br>
Gensim is desigbed to process raw and unstructure digital texts ("plain text") using unsupervised machine learning
"""

import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn import  metrics
import gensim

# Setup training devices
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

#from google.colab import drive
#drive.mount('/content/gdrive')
#file = '/content/gdrive/My Drive/Colab Notebooks/df_text_eng.csv'

ks_data = pd.read_csv('df_text_eng.csv')

lab =  LabelEncoder() # convert fail to 0 and success to 1
ks_data['state'] = lab.fit_transform(ks_data['state'])

ks_data['blurb'] = ks_data['blurb'].values.astype('U') # ensure all blurbs are strings

blurb_split = ks_data.blurb.apply(gensim.utils.simple_preprocess)   #Convert a document into a list of tokens.
bl=[0]*ks_data.shape[0]
for i in range(0,ks_data.shape[0]):
    temp = blurb_split[i]
    bl[i]=''.join(str(temp))

print(bl[1])

countVec = CountVectorizer()
gen = countVec.fit_transform(bl) #Convert text to a matrix of token counts

# split into test and train
X_train, X_val, y_train, y_val = train_test_split(
    gen, ks_data['state'], random_state = 42)

# Apply logistic regression on pre-processing data
from sklearn.linear_model import LogisticRegression

clf=LogisticRegression()
clf.fit(X_train,y_train)

pred1=clf.predict(X_val)
pred_prob1 = clf.predict_proba(X_val)

fpr, tpr, thresholds = metrics.roc_curve(y_val, pred1, pos_label=1)
print('Acuracy: {:.4f}, Log loss: {:.4f}, AUC: {:.4f}.'
.format(metrics.accuracy_score(pred1,y_val), metrics.log_loss(y_val, pred_prob1), metrics.auc(fpr, tpr)))

# Apply Naive Bayes on pre-processing data
from sklearn.naive_bayes import BernoulliNB
mod = BernoulliNB()
mod.fit(X_train, y_train)

pred2 = mod.predict(X_val)
pred_prob2 = mod.predict_proba(X_val)

fpr, tpr, thresholds = metrics.roc_curve(y_val, pred2, pos_label=1)
print('Acuracy: {:.4f}, Log loss: {:.4f}, AUC: {:.4f}.'
.format(metrics.accuracy_score(pred2,y_val), metrics.log_loss(y_val, pred_prob2),metrics.auc(fpr, tpr)))

"""## Long short-term memory (LSTM)"""

import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import torch
import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

# Setup training devices
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

from google.colab import drive
drive.mount('/content/gdrive')
file = '/content/gdrive/My Drive/Colab Notebooks/df_text_eng.csv'
ks_data = pd.read_csv(file)

ks_data = ks_data[['blurb','state']]
ks_data['blurb'] = ks_data['blurb'].values.astype('U')  #change all blurbs to string

# Clean data
ks_data.dropna(axis=0, thresh=None, subset=None, inplace=False)
ks_data.blurb = ks_data['blurb'].str.replace('\W', ' ') #replace special character
ks_data.blurb = ks_data.blurb.str.lower()

# convert fail to 0 and success to 1
lab =  LabelEncoder()
ks_data['state'] = lab.fit_transform(ks_data['state'])

tokenizer = Tokenizer(num_words=2000, split=' ')
tokenizer.fit_on_texts(ks_data['blurb'].values)
bl = tokenizer.texts_to_sequences(ks_data.blurb)
bl = pad_sequences(bl)

lstm_mod = Sequential()
lstm_mod.add(Embedding(2000, 150,input_length = bl.shape[1]))
lstm_mod.add(LSTM(200, dropout=0.2, recurrent_dropout=0.2))
lstm_mod.add(Dense(2,activation='softmax'))
lstm_mod.compile(loss = 'binary_crossentropy', optimizer='adam',metrics = ['accuracy'])

stat = pd.get_dummies(ks_data.state)
X_train, X_val, y_train, y_val = train_test_split(bl, stat, test_size = 0.2, random_state = 42)
lstm_mod.fit(X_train, y_train,validation_data = (X_val,y_val),epochs = 5, batch_size=120)