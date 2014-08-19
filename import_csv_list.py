# -*- coding: utf-8 -*-
import csv
import requests
import pprint
import time
import re
from google_key import google_api_key

def get_google_component_type(address_components, type):
	for component in address_components:
		if(component['types'].__contains__(type)):
			return component

smartadresse_api_key = 'FCF3FC50-C9F6-4D89-9D7E-6E3706C1A0BD'

csv_file = open('codingpirates_medlemmer.csv', 'r')

medlemmer = csv.reader(csv_file)
medlemmer.next() #skip 1st. line

for medlem in medlemmer:
	orgAddress = medlem[2];

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
		if(roadnumber == None):
			roadnumber = ''
	# components might be None as well!

	# begin by smart looking up the streetname (might be speed different)
	#url = 'https://smartadresse.dk/service/locations/3/streetname/json/' + streetname
	#params = {'apikey' : smartadresse_api_key, 'limit' : 10}
	#if(len(postal) == 4):
	#	params['area'] = postal
	#response = requests.get(url, params=params)
	#decoded_response = response.json()
	#print(response.text)

	url = 'https://maps.googleapis.com/maps/api/geocode/json'
	params = {'key' : google_api_key, 'region' : 'dk', 'address' : streetname + roadnumber + ', ' + postal}
	if(len(postal) == 4):
		params['postal_code'] = postal
	response = requests.get(url, params=params)
	decoded_response = response.json()

	google_streetname = get_google_component_type(decoded_response['results'][0]['address_components'], 'route')['long_name']
	google_postal = get_google_component_type(decoded_response['results'][0]['address_components'], 'postal_code')['long_name']

	# First look up in AWS cleartext search
	url = 'http://dawa.aws.dk/adresser'
	params = {'q' : orgAddress}
	response = requests.get(url, params=params)

	decoded_response = response.json()

	aws_found = False
	if(len(decoded_response) == 1):
		print(' ORG:' + orgAddress)
		print(' AWS:' + decoded_response[0]['adressebetegnelse'])
		aws_found = True
	else:
		# not found - try smarter - use roadname from google lookup
		url = 'http://dawa.aws.dk/adresser'
		query = google_streetname + ' ' + roadnumber + ', ' + floor_door
		if(len(postal) == 4):
			# use postal from original
			query = query + ' ' + postal
		elif(len(google_postal) == 4):
			# no original postal - use the one from google guess
			query = query + ' ' + google_postal

		params = {'q' : query}
		response = requests.get(url, params=params)

		decoded_response = response.json()

		print('gQ  : ' + query)

		if(len(decoded_response) == 1):
			print('gORG:' + orgAddress)
			print('gAWS:' + decoded_response[0]['adressebetegnelse'])
			aws_found = True
		else:
			print('!ORG:' + orgAddress)
			print('!AWS: **********************************************')

	if(aws_found):
		final_roadname = decoded_response[0]['adgangsadresse']['vejstykke']['navn']
		final_roadnumber = decoded_response[0]['adgangsadresse']['husnr']
		final_postal = decoded_response[0]['adgangsadresse']['postnummer']['nr']
		final_city = decoded_response[0]['adgangsadresse']['postnummer']['navn']
		final_floor = decoded_response[0]['etage']
		final_door = decoded_response[0][u'd\xf8r']
		final_uuid = decoded_response[0]['id']

	time.sleep(1) # dont spam aws.dk
	print('')
