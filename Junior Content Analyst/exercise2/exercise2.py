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
	df = df.rename(columns={'index': 'fullname'})
	df.to_csv('data_csv.csv', index=False)

	# Exercise 2 part 2
	# Generate statistics with the data collected and save to a JSON

	# statistics based on the last name which we retrieve by getting unique entries on df above
	# for each last name we will add a dictionary entry on d before finally writing the json output file
	last_names = df.fullname.map(lambda x: x.split(' '), na_action='ignore').str[1].unique()
	d = {}
	for last_name in last_names:
		filtered_df = df[df.fullname.str.contains(last_name)]
		count = filtered_df.fullname.count()
		ages = {str(x): filtered_df[filtered_df.age == x].age.count() for x in filtered_df.age.unique()}
		addresses = {x: filtered_df[filtered_df.address == x].address.count() for x in filtered_df.address.unique()}
		occupations = {x: filtered_df[filtered_df.occupation == x].occupation.count() for x in filtered_df.occupation.unique()}
		d[last_name] = {'count': count, 'age': ages, 'address': addresses, 'occupation': occupations}

	# write the data to a json file using pretty print.
	pd.DataFrame(data=d).to_json('output.json', indent=4)
