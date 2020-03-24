#!usr/bin/python3

# use selenium to collect data from websites using dynamic data.
from selenium import webdriver
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer  # stemmer to be used on list of words

import os

SHOW = True  # Flag to show text when running the code
SLEEP = 0  # sleep time when opening pages with selenium
# FILE_WEBSITES = 'gambling.txt'
SITES_DIR = './websites/'
DICTS_DIR = './dictionaries/'
# whitelist of html elements to parsed
whitelist = [
    'h1', 'h2', 'h3',
    'h4', 'h5', 'h6',
    'p', 'ul', 'li',
    'ol', 'div', 'table',
]

# common tags from angular etc. as well as words that may be common but not related to the context such as:
# user, end, site, orderby etc..
exclude_list = [
    'ngif', 'ngrepeat', 'id', 'nginclude', 'html',
    'itemgroup', 'num', 'localeindex', 'limitto',
    'locales', 'itemevent', 'http', 'uiview',
    'uid', 'uuidc', 'orderby', 'end', 'begin',
    'cookies', 'site', 'xml', 'ad'
]


def tokenize_and_stem(text_list):
    """
    :param text_list: list of input texts from the webpages
    :return: stemmed and tokenized word list
    """
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

    if SHOW:
        print('SETTING UP CHROMEDRIVER')
    # setup selenium using Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('incognito')
    options.add_argument('headless')
    # location of chrome driver using chrome on windows v.80
    browser = webdriver.Chrome(executable_path='../chromedriver/chromedriver.exe', options=options)

    sites_files = os.listdir(SITES_DIR)  # files with sites for each category

    # open the text file and read the websites into the websites list
    for site_file in sites_files:

        websites = []  # websites will store the list of websites to be visited
        texts = []  # texts will store the strings with the texts found on each website
        aggregate = []  # aggregate will store the final list with all the stemmed and cleaned values.
        cat = site_file.split('.')[0]
        with open(SITES_DIR+site_file) as f:
            websites = [line.rstrip() for line in f]

        if SHOW:
            print(f'Start category: {cat} ')

        # check each website and collect the visible text
        for i, website in enumerate(websites):
            if SHOW:
                print(f'website {i+1} of {len(websites)}: {website}')

            # using Selenium to call Chrome and parse the text using bs4
            browser.get(website)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            text = soup.find_all(text=True)
            # put all the words found on the website to a string
            output = ''
            for t in text:
                # work with a whitelist of elements to read
                if t.parent.name in whitelist:
                    t = t.strip('\t\r\n')
                    if t != '':
                        output += t+' '
            # Convert the collected data to lowercase and split on spaces
            output = output.lower().split()
            for word in output:
                texts.append(word)

        if SHOW:
            print('creating a dictionary')
        try:
            aggregate = tokenize_and_stem(texts)
        except LookupError:
            # The program throws an exception if the packages are not installed
            nltk.download('punkt')
            nltk.download('stopwords')
            aggregate = tokenize_and_stem(texts)

        # find the most frequent entries
        aggregate = nltk.FreqDist(aggregate)
        # define the size of the dictionary and extract only the terms that are most common
        n_features = 1000
        features = aggregate.most_common(n_features)

        # write to a csv file
        csv = cat+'_dictionary.csv'
        with open(DICTS_DIR+csv, 'w', encoding='utf-8') as csv_file:
            csv_file.write('entry,occurrences\n')
            for key, value in features:
                csv_file.write(f'{key},{value}\n')

        if SHOW:
            print(f'End category: {cat}\n')

    browser.close()
