#!/usr/bin/python3

# Read the JSON file and convert to a CSV with the following format:
# fullname, age, address, occupation

import pandas as pd

if __name__ == '__main__':

	# Exercise 2 Part 1
	# Read the JSON file to a DataFrame
	df = pd.read_json('data.json', orient='records')
	# The orientation needs to be changed so we transpose the DataFrame
	df = df.T.reset_index()  
	df = df.rename(columns = {'index':'fullname'})
	df.to_csv('data.csv', index=False)

	# Exercise 2 part 2
	# Generate statistics with the data collected and save to a JSON
	