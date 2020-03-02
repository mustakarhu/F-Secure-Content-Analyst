#!/usr/bin/python3

import sys
from bs4 import BeautifulSoup
import requests


def main():
	"URL checker."
	assert (len(sys.argv)==2), "Invalid input format."
	page = requests.get(sys.argv[1]).text
	soup = BeautifulSoup(page, features='lxml')
	for link in soup.find_all('a'):
		print(link.get('href'))



if __name__ == '__main__':
	main()