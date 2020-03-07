#!usr/bin/python3

# use selenium to collect data from websites using dynamic data.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import urllib.request

FILE_WEBSITES = 'example.txt' #'gambling.txt'
SLEEP = 5


if __name__ == '__main__':

    # setup selenium using Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('incognito')
    # options.add_argument('headless')

    # location of chrome driver using chrome on windows v.80
    browser = webdriver.Chrome(executable_path='../chromedriver/chromedriver.exe', options=options)

    # open the text file and read the websites into the websites list
    websites = []
    with open(FILE_WEBSITES) as f:
        websites = [line.rstrip() for line in f]

    for website in websites:
        browser.get(website)
        time.sleep(SLEEP)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        text = soup.find_all(text=True)
        output = ''
        blacklist = [
            '[document]',
            'noscript',
            'header',
            'html',
            'meta',
            'head',
            'input',
            'script',
            'button',
            'style',

            'span',
            'body',
            'nav',
            'footer',
            'section',
            # 'ul',
            # 'ol',
            'ui-view',
            'li',
            'div',
            'h1',
            'h2',
            'h3',
            'a',
            'p',
            'main',
            'strong',
            'title',
            # there may be more elements you don't want, such as "style", etc.
        ]
        output = []
        for t in text:
            if t.parent.name not in blacklist:
                # print(t.parent.name)
                t = t.strip('\t\r\n')
                if t != '':
                    output.append(f'{t}')
        print(output)
        # for entry in output:
        #     print(entry)
    browser.close()

