import matplotlib.pyplot as plt
import numpy as np
import operator
import json
import sys
import urllib.request
import hashlib
import os
import csv
import re
from string import punctuation

list_of_countries = {}
country_to_count = {}
patterns = {}

def construct_country_objects():
	f = open('countries.json')
	data = json.loads(f.read())
	f.close()

	for row in data:
		row.pop('num_code', None)
		row['cities'] = {}
		row['province'] = {}
		list_of_countries[row['en_short_name']] = row
		country_to_count[row['en_short_name']] = 0
		patterns[row['en_short_name']] = re.compile("(^|\s)" + row['en_short_name'] + "(\s|$)")
		patterns[row['alpha_2_code']] = re.compile("(^|\s)" + row['alpha_2_code'] + "(\s|$)")
		patterns[row['alpha_3_code']] = re.compile("(^|\s)" + row['alpha_3_code'] + "(\s|$)")
		
	
	f = open('extra_countries.json')
	data = json.loads(f.read())
	f.close()

	for row in data:
		row['cities'] = {}
		row['province'] = {}
		list_of_countries[row['en_short_name']] = row
		country_to_count[row['en_short_name']] = 0
		patterns[row['en_short_name']] = re.compile("(^|\s)" + row['en_short_name'] + "(\s|$)")
		
def populate_cities():
	f = open('cities.csv')
	reader = csv.reader(f, delimiter=',')
	next(reader)
	for row in reader:
		# 0 = city
		# 1 = city_ascii
		# 2 = lat
		# 3 = long
		# 4 = pop
		# 5 = country
		# 6 = iso2
		# 7 = iso3
		# 8 = province	
		if row[5] in list_of_countries:
			list_of_countries[row[5]]['cities'][row[1]] = int(float(row[4]))
			
			if row[8] not in list_of_countries[row[5]]['province']:
				list_of_countries[row[5]]['province'][row[8]] = int(float(row[4]))
			else:
				list_of_countries[row[5]]['province'][row[8]] += int(float(row[4]))
			patterns[row[1]] = re.compile("(^|\s)" + row[1] + "(\s|$)")
			patterns[row[8]] = re.compile("(^|\s)" + row[8] + "(\s|$)")
		else:
			print("Country excluded from dataset: " + row[5])

def check_mentions(title):
	title = ''.join(c for c in title if c not in punctuation)
	
	# check if country or code is in title
	for key in list_of_countries:
		pattern = patterns[key]
		if re.search(pattern, title) \
			or ('alpha_3_code' in list_of_countries[key] and re.search(patterns[list_of_countries[key]['alpha_3_code']], title)) \
			or ('alpha_2_code' in list_of_countries[key] and re.search(patterns[list_of_countries[key]['alpha_2_code']], title)) \
			or list_of_countries[key]['nationality'] in title:
				print("Found: " + key)
				country_to_count[key] += 1
				return

	# check if city or province in the title
	country_city = ""
	country_province = ""
	city_name = ""
	province_name = ""
	city_name_length = 0
	city_population = 0
	province_name_length = 0
	province_population = 0

	for key in list_of_countries:
		for city in list_of_countries[key]['cities']:
			pattern = patterns[city]
			if re.search(pattern, title):
				if list_of_countries[key]['cities'][city] > city_population:
					country_city = key
					city_name = city
					city_name_length = len(city)
					city_population = list_of_countries[key]['cities'][city]

		for province in list_of_countries[key]['province']:
			pattern = patterns[province]
			if re.search(pattern, title):
				if list_of_countries[key]['province'][province] > province_population:
					country_province = key
					province_name = province
					province_name_length = len(province)
					province_population = list_of_countries[key]['province'][province]

	if len(city_name) > 0 and city_name_length >= province_name_length and country_city in list_of_countries:
		country_to_count[country_city] += 1
		print("Found: " + country_city + "		City:" + city_name)
	elif len(province_name) > 0 and country_province in list_of_countries:
		country_to_count[country_province] += 1
		print("Found: " + country_province + "		Province: " + province_name)

def plot_reddit_most_loved_country():
	x_axis_objects = []
	y_axis_values = []

	# merge england and great britain together, because both are used almost equally
	uk = country_to_count['England'] + country_to_count['Britain'] + country_to_count['United Kingdom']
	country_to_count['United Kingdom'] = uk
	del country_to_count['England']
	del country_to_count['Britain']

	s = [(k, country_to_count[k]) for k in sorted(country_to_count, key=country_to_count.get, reverse=True)]	

	i = 0
	for k, v in s:
		if i >= int(sys.argv[3]):
			break
		x_axis_objects.append(k)
		y_axis_values.append(v)
		i += 1

	plt.barh(np.arange(len(x_axis_objects)), y_axis_values, align='center', alpha=0.5)
	plt.yticks(np.arange(len(x_axis_objects)), x_axis_objects)
	plt.xlabel('Number of times mentioned')
	plt.title('Number of times a country is mentioned in /r/' + sys.argv[1] + '/' + sys.argv[2] + ' posts')
	plt.tight_layout()
	plt.gca().invert_yaxis()
	plt.show()

if __name__ == "__main__":
	if str(sys.argv[1]) == "help":
		print("python3 redditr.py <subreddit> <top/controversial/hot> <integer: top N results>")
		exit(1)

	construct_country_objects()

	populate_cities()

	print("Completed setup!")

	header = {'User-Agent': str(hashlib.md5(os.urandom(32)).hexdigest())}
	url = "https://www.reddit.com/r/" + str(sys.argv[1]) + "/" + str(sys.argv[2]) + "/.json?t=all&limit=100&count=100"

	after = ""
	get_request = ""
	count = 1
	for i in range(0, 10):
		to_request = url + after
		req = urllib.request.Request(to_request, data=None, headers=header)
		contents = urllib.request.urlopen(req).read()
		parsed = json.loads(contents.decode('utf-8'))
		after = "&after=" + str(parsed['data']['after'])
		for child in parsed['data']['children']:
			print(str(count) + ". " + child['data']['title'])
			check_mentions(child['data']['title'])
			count += 1

	s = [(k, country_to_count[k]) for k in sorted(country_to_count, key=country_to_count.get, reverse=True)]
	for k, v in s:
		if v == 0:
			break	
		print(k + " " + str(v))

	plot_reddit_most_loved_country()
