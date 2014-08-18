# -*- coding: utf-8 -*-
import csv
import requests
import pprint
import time
import re

csv_file = open('codingpirates_medlemmer.csv', 'r')

medlemmer = csv.reader(csv_file)
medlemmer.next() #skip 1st. line

for medlem in medlemmer:
	orgAddress = medlem[2];
	print("oprindelig adresse data: " + orgAddress)

	# clean address from double whitespaces and newlines
	conditionedAddress = re.sub('\n',' ', orgAddress)
	conditionedAddress = re.sub(' +',' ', conditionedAddress)

	# Get roadname, number and postal code from address
	m = re.search(r'^(?P<streetname>(?: *[a-zA-ZÆØÅæøå.é]+)+) {0,1}(?:(?P<streetnumber>\d+[ ]{0,1}[a-zA-ZÆØÅæøå]*)(?:[ ,]|$)){0,1} ?,? ?(?P<floor_door>.*?) ?,? ?(?P<postal>(?:[0-9]{4}){0,1})(?:[a-zA-ZÆØÅæøå.]+|[ ])*?$', conditionedAddress)
	if(m != None):
		streetname = m.group('streetname')
		roadnumber = m.group('streetnumber')
		floor_door = m.group('floor_door')
		postal     = m.group('postal')
	# components might be None as well!

	url = 'http://dawa.aws.dk/adresser'
	params = {'q' : orgAddress}
	response = requests.get(url, params=params)

	decoded_response = response.json()

	#print(response.status_code)
	#print(response.text)

	if(len(decoded_response) == 1):
		print("                       : " + decoded_response[0]['adressebetegnelse'])
	#else:
		# not found - try smarter

	time.sleep(1) # dont spam aws.dk
	print('')
