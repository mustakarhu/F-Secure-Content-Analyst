#!/usr/bin/python3


import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests
SLEEP = 0
protocol = ('http:', 'https:')


class Weblinks():

    def __init__(self, URL: str):
        self.URL = URL[:-1] if URL.endswith('/') else URL
        self.TLD = ''
        self.hostname = ''
        self.domain = ''
        self.path = ''
        # 0 - hostname, 1 - domain , 2 - external
        self.links = [[], [], []]

    def getlinks(self):
        s = self.URL.split('/')
        # this part will collect the TLD, hostname, domain as well as current path.
        for entry in s:
            if entry.lower() not in protocol:
                # we enter in this condition if we are visiting the array for the first time.
                if self.TLD == '':
                    url = entry.split('.')
                    self.TLD = url[-1]
                    self.hostname = entry
                    self.domain = '.'.join(url[1:]) if len(url) > 2 else entry
                else:
                    self.path += '/' + entry

        # collect the links on the page via requests HTML
        options = webdriver.ChromeOptions()
        options.add_argument('incognito')
        options.add_argument('headless')
        browser = webdriver.Chrome(executable_path='../chromedriver/chromedriver.exe', options=options)
        browser.get(self.URL)
        time.sleep(SLEEP)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.close()

        # possible href values to be ignored
        ignore_list = [None, '#', 'javascript']
        for link in soup.find_all('a'):
            # get the links
            href = link.get('href')
            if href not in ignore_list:
                # fully qualified url
                if href.startswith(protocol) and href not in self.links:
                    # analyze the beginning of the url so we don't classify erroneously if hostname or domain
                    # appears in a query for example
                    filtered_href = href.split('#')[0].split('?')[0]
                    loc = 0 if self.hostname in filtered_href else 1 if self.domain in filtered_href else 2
                    self.links[loc].append(href)
                    # print(href)

                # if url inherits protocol it will start with // without leading protocol name
                elif href.startswith('//') and self.URL.split('//')[0]+href not in self.links[0]:
                    # analyze the beginning of the url so we don't classify erroneously if hostname or domain
                    # appears in a query for example
                    filtered_href = href.split('#')[0].split('?')[0]
                    loc = 0 if self.hostname in filtered_href else 1 if self.domain in filtered_href else 2
                    self.links[loc].append(self.URL.split('//')[0]+href)
                    # print(href)

                # not fully qualified url -> go to top level domain
                elif href.startswith('/') and len(href) > 1:
                    if href[1:].startswith(protocol) and href[1:] not in self.links[0]:
                        loc = 0 if self.hostname in href else 1 if self.domain in href else 2
                        self.links[loc].append(href[1:])

                    elif self.URL+href not in self.links[0]:
                        self.links[0].append(self.URL+href)

                # not fully qualified url without leading / -> go to child page
                else:
                    if self.URL+href not in self.links[0]:
                        self.links[0].append(self.URL+href)
                        # print(self.URL+href)

            # remove duplicates
            self.links[0] = list(set(self.links[0]))
            self.links[1] = list(set(self.links[1]))
            self.links[2] = list(set(self.links[2]))

    def output(self):
        print(f'TLD: {self.TLD}\nDOMAIN: {self.domain}\nHOSTNAME: {self.hostname}\nPATH: {self.path}\nLINKS:')
        print('\n'+4*' '+'Same Hostname:')
        for entry in self.links[0]:
            print(8*' '+entry)
        print('\n'+4*' '+'Same domain:')
        for entry in self.links[1]:
            print(8*' '+entry)
        print('\n'+4*' '+'Different domain:')
        for entry in self.links[2]:
            print(8*' '+entry)


if __name__ == '__main__':
    assert (len(sys.argv) == 2), "Invalid input format. Please include URL as input parameter"
    web = Weblinks(sys.argv[1])
    web.getlinks()
    web.output()


