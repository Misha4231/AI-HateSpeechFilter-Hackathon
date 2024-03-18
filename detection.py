from nltk.util import pr
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
import re
import nltk
from nltk.corpus import stopwords
import string
import datetime
from googletrans import Translator
from allowedCategories import AllowedCategories

nltk.download('stopwords')
stemmer = nltk.SnowballStemmer("english")
stopword = set(stopwords.words('english'))


badWords = pd.read_csv('trainData/badWords.csv')
data = pd.read_csv("trainData/tweeter1.csv")


# data["class"] 0 = "Hate Speech", 1 = "Offensive Language", 2 = "No Hate and Offensive"

def clean(text):
    text = str(text).lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = [word for word in text.split(' ') if word not in stopword]
    text=" ".join(text)
    text = [stemmer.stem(word) for word in text.split(' ')]
    text=" ".join(text)
    return text


data["text"] = data["tweet"].apply(clean)

x = np.array(data["tweet"])
y = np.array(data["class"])

cv = CountVectorizer()
X = cv.fit_transform(x) 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=55)

clf = LogisticRegression()
clf.fit(X_train,y_train)


def detectHate(sample):
    data = cv.transform([sample]).toarray()
    prediction = clf.predict(data)[0]
    
    offensiveWords = []

    if prediction in [0, 1]:
        nonzero_idx = np.nonzero(data)[1]

        for idx in nonzero_idx:
            pottentianWord = cv.get_feature_names_out()[idx]

            for badWordIdx in range(len(badWords['text'])):
                if pottentianWord == badWords['text'][badWordIdx]:
                    offensiveWords.append([badWords['text'][badWordIdx], badWords['category_1'][badWordIdx]])
                    break

                if pottentianWord == badWords['canonical_form_1'][badWordIdx]:
                    offensiveWords.append([badWords['canonical_form_1'][badWordIdx], badWords['category_1'][badWordIdx]])
                    break


    for pottentianWord in sample.split(' '):

        for badWordIdx in range(len(badWords['text'])):
            if pottentianWord == badWords['text'][badWordIdx]:
                offensiveWords.append([badWords['text'][badWordIdx], badWords['category_1'][badWordIdx]])
                break

            if pottentianWord == badWords['canonical_form_1'][badWordIdx]:
                offensiveWords.append([badWords['canonical_form_1'][badWordIdx], badWords['category_1'][badWordIdx]])
                break

    if prediction == 2 and len(offensiveWords) > 0:
        prediction == 1
    return [prediction, offensiveWords]
