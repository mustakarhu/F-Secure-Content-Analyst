#!/usr/bin/python3

import sys
from bs4 import BeautifulSoup
import requests


protocol = ['http:', 'https:']

class datastream():
	
	def __init__(self, URL:str):
		self.URL = URL
		self.TLD = ''
		self.hostname = ''
		self.domain = ''
		self.path = ''
		self.links = ['','','']
		self.c1 = [[],[],[]]


	def getlinks(self):
		
		s = self.URL.split('/')
		

		# this part will collect the TLD, hostname, domain as well as current path.
		for entry in s:
			if entry.lower() not in protocol:
				# we enter in this condition if we are visiting the array for the first time.
				if (self.TLD == ''):
					url = entry.split('.')
					self.TLD = url[-1]
					self.hostname = entry 
					self.domain = '.'.join(url[1:]) if len(url) > 2 else entry
				else:
					self.path+='/'+entry

		# collect the links on the page via requests HTML

		page = requests.get(sys.argv[1]).text
		soup = BeautifulSoup(page, features='lxml')
		for link in soup.find_all('a'):
			href = link.get('href')
			if href is not None and not href.startswith('#'):
				# relative paths of the same hostname
				if href.startswith('/'):
					if href not in self.c1[0]:
						self.c1[0].append(href)

				elif self.hostname in href:
					if href not in self.c1[0]:
						self.c1[0].append(href)

				#links on the same domain
				elif self.domain in href: 
					if href not in self.c1[1]:
						self.c1[1].append(href)

				#links from a different domain
				elif href not in self.c1[2]:
					self.c1[2].append(href)







	def output(self	):
		print(f'TLD: {self.TLD}\nDOMAIN: {self.domain}\nHOSTNAME: {self.hostname}\nPATH: {self.path}\nLINKS:')
		print(f'  Same Hostname:')
		for entry in self.c1[0]:
			print('    '+self.hostname+entry)
		print('   Same domain:')
		for entry in self.c1[1]:
			print('    '+entry)
		print('   External domain:')
		for entry in self.c1[2]:
			print('    '+entry)


def main():
	"URL checker."
	assert (len(sys.argv)==2), "Invalid input format."
	ds = datastream(sys.argv[1])
	ds.getlinks()
	ds.output()


if __name__ == '__main__':
	main()