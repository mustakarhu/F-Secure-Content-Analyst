#!usr/bin/python3

import sys
from selenium import webdriver
from selenium.common import exceptions
from bs4 import BeautifulSoup
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from sklearn.svm import OneClassSVM
from sklearn.feature_extraction.text import TfidfVectorizer

SHOW_OUTPUT = False

# whitelist of elements to parsed
whitelist = [
    'h1', 'h2', 'h3',
    'h4', 'h5', 'h6',
    'p', 'ul', 'li',
    'ol', 'div', 'table',
    'title'
]

exclude_list = [
    'ngif', 'ngrepeat', 'id', 'nginclude', 'html',
    'itemgroup', 'num', 'localeindex', 'limitto',
    'locales', 'itemevent', 'http', 'uiview',
    'uid', 'uuidc', 'orderby', 'end', 'begin',
    'cookies', 'site',
]


def tokenize_and_stem(text_list):
    stop_words = set(stopwords.words('english'))
    words = []
    for e in text_list:
        words += word_tokenize(e)
    # remove punctuations, stopwords, irrelevant terms (see above exclude_list) and numbers
    words = [w for w in words if w.isalpha()]
    words = [w for w in words if w not in stop_words]
    words = [w for w in words if w not in exclude_list]
    words = [w for w in words if not w.isdigit()]
    # stem the words using the Snowball stemmer
    stemmer = SnowballStemmer('english')
    stemmed = [stemmer.stem(w) for w in words]
    return stemmed


if __name__ == '__main__':
    assert len(sys.argv) == 2, "Invalid input format. Please include the URL name to be evaluated as an input argument"
    URL = sys.argv[1]
    # read dictionary
    dictionary = pd.read_csv('dictionary.csv')

    if SHOW_OUTPUT:
        print('setting up Selenium Chromedriver')
    # setup selenium using Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('incognito')
    options.add_argument('headless')
    # location of chrome driver using chrome on windows v.80
    browser = webdriver.Chrome(executable_path='../chromedriver/chromedriver.exe', options=options)
    try:
        if SHOW_OUTPUT:
            print('fetching URL')
        browser.get(URL)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        text = soup.find_all(text=True)
        browser.close()
    except exceptions.InvalidArgumentException:
        print('invalid URL')
        raise

    output = ''
    for t in text:
        # work with a whitelist of elements to read
        if t.parent.name in whitelist:
            t = t.strip('\t\r\n')
            if t != '':
                output += t + ' '
    output = output.lower().split()
    aggregate = []
    try:
        aggregate = tokenize_and_stem(output)
    except LookupError:
        # The program throws an exception if the packages are not installed
        nltk.download('punkt')
        nltk.download('stopwords')
        aggregate = tokenize_and_stem(output)

    # find the most frequent entries
    aggregate = nltk.FreqDist(aggregate)

    # scoring of entries.
    score = 0
    total_score = len(aggregate.keys())

    for word in aggregate.keys():
        if word in dictionary.entry.tolist():
            score += 1

    # if more than 2/3 of the words are found returns as a Gambling website
    x = 'Gambling Site' if score/total_score > 0.66 else 'Not Gambling site'
    print(x)
    if SHOW_OUTPUT:
        print(f'score: {score/total_score}')

    # # possible improvement - using one-class SVM.
    # vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 1), sublinear_tf=True)
    # X = vectorizer.fit_transform(dictionary[dictionary.entry.notna()])
    # data_features = vectorizer.fit_transform(dictionary[dictionary.entry.notna()])
    # clf = OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
    # clf.fit(data_features)
    # test_data_features = vectorizer.transform(pd.Series(list(aggregate.keys())))
    # if SHOW_OUTPUT:
    #     print(clf.predict(test_data_features))
    #     print(clf.decision_function(test_data_features))



