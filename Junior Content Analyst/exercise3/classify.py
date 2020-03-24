
from selenium import webdriver
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import sys
import os
import numpy as np
import pandas as pd
from random import choices, seed
import pickle


input_arg = "https://www.bbc.com/news"
whitelist = [
    'h1', 'h2', 'h3',
    'h4', 'h5', 'h6',
    'p', 'ul', 'li',
    'ol', 'div', 'table',
]

# common tags from angular etc. as well as words that may be common but not related to the context such as:
# user, end, site, orderby etc..
exclude_list = set([
    'ngif', 'ngrepeat', 'id', 'nginclude', 'html',
    'itemgroup', 'num', 'localeindex', 'limitto',
    'locales', 'itemevent', 'http', 'uiview',
    'uid', 'uuidc', 'orderby', 'end', 'begin',
    'cookies', 'site', 'xml', 'ad'
])


def get_features_list(list_of_words, dictionary):
    """
    :param list_of_words: most common words found on the website
    :param dictionary: dictionary of words we want to compare against
    :return: features dictionary to be used for classification
    """
    d = set(dictionary)
    w = set(list_of_words)
    x = {}
    for word in d:
        x[word] = word in list_of_words
    return x


if __name__ == '__main__':

    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument('headless')
    browser_options.add_argument('incognito')
    browser_options.add_argument('disable-gpu')

    non_gambling_sites_file = 'sites_file.txt'
    gambling_sites_file = 'gambling_sites_file.txt'

    df_dict = pd.read_csv('./dictionaries/gambling_dictionary.csv', encoding='utf-8')
    dict_features = df_dict.entry.tolist()[:100]
    d = {'X': [], 'y': []}
    df = pd.DataFrame(data=d)
    df.X.astype(object)

    with open(non_gambling_sites_file, 'r') as f:
        websites = [(line.rstrip(), 0) for line in f]
        websites = choices(websites, k=60)

    with open(gambling_sites_file, 'r') as f:
        gambling_sites = [(line.rstrip(), 1) for line in f]
        seed(1)
        websites += choices(gambling_sites, k=40)

    i = 1
    for website in websites:
        print(f"site: {i} of {len(websites)} ", website)
        browser = webdriver.Chrome(executable_path="../chromedriver/chromedriver.exe", options=browser_options)
        url = website[0]
        label = website[1]
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        text = soup.find_all(text=True)
        output = ''
        words = []
        stop_words = set(stopwords.words('english'))
        for element in text:
            if element.parent.name in whitelist:
                element = element.strip('\n\t')
                if str(element):
                    element = element.lower()
                    element_list = element.split()
                    element_list = [word for word in element_list if word not in stop_words]
                    element_list = [word for word in element_list if word not in exclude_list]
                    words += element_list

        N = 100
        frequency_distribution = nltk.FreqDist(words)
        bow_dict = frequency_distribution.most_common(N)[:100]
        bow = [occurrence[0] for occurrence in bow_dict]
        X = get_features_list(bow, dict_features)
        y = label
        d = {'X': [X], 'y': y}
        df = pd.concat([df, pd.DataFrame(data=d)])
        browser.close()
        i+=1

    df.sample(n=len(df), random_state=47)
    X = df.X.tolist()
    y = df.y.tolist()
    feature_set = [(X[i], y[i]) for i in range(len(X))]
    train_features = feature_set[:70]
    test_features = feature_set[70:]
    clf = nltk.NaiveBayesClassifier.train(train_features)
    print("accuracy:", nltk.classify.accuracy(clf, test_features))

    
    with open('naivebayes_nltk.pickle', 'wb') as f:
        pickle.dump(clf, f)
