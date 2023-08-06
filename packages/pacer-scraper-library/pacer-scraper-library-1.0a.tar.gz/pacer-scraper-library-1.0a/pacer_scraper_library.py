import codecs
import csv
import os
import pickle
import re
import time
import urllib

import mechanize
from bs4 import BeautifulSoup
import lxml

__all__=['codecs', 'csv', 'os', 'pickle', 're', 'time', 'urllib', 'mechanize', 
		 'BeautifulSoup', 'lxml', 'login_to_pacer', 'create_PACER_query', 
		 'download_docket_sheet', 'parse_docket', 'parse_docket_dir', 
		 'copy_docket', 'download_document']


# We initialize the mechanize browser (ignore robots.txt).
br=mechanize.Browser()
br.set_handle_robots(False)
br.set_handle_referer(True)
br.set_handle_refresh(True)


def login_to_pacer(username, password):		
	br.open("https://pacer.login.uscourts.gov/cgi-bin/login.pl")
	br.select_form(nr = 0)
	br["loginid"] = username
	br["passwd"] = password
	br.submit()
	
	if "Case Search Login Error" in br.response().get_data():
		raise ValueError("Could not login to PACER Case Search. Check your "
						 "username and password")
	print ("You are logged on to the Public Access to Court Electronic "
		   "Records (PACER) Case Search website as "+ username + ". All costs "
		   "will be billed to this account.")
	return br

# District variable example: "ED NY"
# [NOT IMPLEMNTED]: Federal courts other than district and bankruptcy courts.
# Be aware that some district courts deal with appeals (indicated 'ap')
# Appellate courts don't use the type-code or office, instead they use 
# [circuit #]-[case #] (e.g., 02-00158)
# Decsision tree --> TYPE CODE --> DISTRICT
def create_PACER_query(district, office, docket_number, type_code):
	type_code_dict = {'civil':'cv', 'civ': 'cv',
					  'criminal': 'cr', 'crim': 'cr',
					  'bankruptcy': 'bk', 'bank': 'bk'}
	state_to_code = {"alaska": "ak", "alabama": "al", "arkansas": "ar", 
					"arizona": "az", "california": "ca", "colorado": "co", 
					"connecticut": "ct", "delaware": "de", 
					"district of columbia": "dc", "florida": "fl", 
					"georgia": "ga", "hawaii": "hi", "iowa": "ia", 
					"idaho": "id", "illinois": "il", 
					"indiana": "in", "kansas": "ks", "kentucky": "ky", 
					"louisiana": "la","maine": "me", "maryland": "md", 
					"massachusetts": "ma", "michigan": "mi", "minnesota": "mn",
					"mississippi": "ms",  "missouri": "mo", "montana": "mt", 
					"nebraska": "ne", "nevada": "nv", "new hampshire": "nh", 
					"new jersey": "nj", "new mexico": "nm", "new york": "ny", 
					"north carolina": "nc", "north dakota": "nd", 
					"northern mariana islands": "nmi", "ohio": "oh", 
					"oklahoma": "ok", "oregon": "or", "pennsylvania": "pa",  
					"puerto rico": "pr", "rhode island": "ri", 
					"south carolina": "sc", "south dakota": "sd", 
					"tennessee": "tn", "texas": "tx", "utah": "ut", 
					"vermont": "vt", "virgin islands": "vi", "virginia": "va", 
					"washington": "wa", "west virginia": "wv", 
					"wisconsin": "wi", "wyoming": "wy", }				
	district_dict = {'northern district': 'nd',
					 'southern district': 'sd',
					 'eastern district': 'ed',
					 'western district': 'wd',
					 'middle district': 'md',
					 'central district': 'cd',
					 'northern bankruptcy': 'nb',
					 'southern bankruptcy': 'sb',
					 'eastern bankruptcy': 'eb',
					 'western bankruptcy': 'wb',
					 'middle bankruptcy': 'mb',
					 'central bankruptcy': 'cb'}
	
	# The program tries to identify the type_code.
	if type_code in type_code_dict.keys():
		type_code=type_code_dict[type_code]
	elif type_code not in ('cr', 'cv', 'bk', 'ap'): 
		return ['ERROR', 'Bad Case Type (type_code)']
	
	district=district.lower().replace(' ','')
	#Using the type-code, we determine the correct suffix.
	if type_code in ('cr', 'cv'): 
		suffix = 'ce'
	elif type_code in 'bk':
		suffix = 'ke'
	elif type_code in 'ap':
		return ['ERROR', 'Appellate Court Queries Not Currently Implemented']
		
	# The program converts the district input into a court_id.
	if district.startswith('dc') and len(district)==4:
		court_id = district[2:4]+'dce'
	elif len(district) == 4:
		court_id = district[2:4]+district[0:2]+suffix
	elif len(district) == 3:
		court_id = district[1:3]+district[0:1]+suffix
	elif len(district) > 4:
		court_id=''
		for key in state_to_code:
			if key.replace(' ', '') in district:
				court_id = state_to_code[key]
				break	
		if not court_id: return ['ERROR', 'Could not determine state']
		
		for key in district_dict:
			if key.replace(' ', '') in district:
				court_id = court_id + district_dict[key]+suffix
				break
		if len(court_id)==2:
			if 'district' in district and 'columbia' not in district:
				court_id=court_id+'d'+suffix
			elif 'bankruptcy' in district:
				court_id=court_id+'b'+suffix
				
		if len(court_id) < 5 or len(court_id) > 6:
			return ['ERROR', 'Could not determine district']
	else:
		return ['ERROR', 'Something is wrong with your district input.']
					
	# Finally, transform the docket number into a year/case_number
	if type_code in ('cv', 'cr', 'bk'): # ca --> circuit court of appeals
		if len(docket_number) == 6:	
			docket_number = '0'+docket_number
		elif len(docket_number) == 5:
			docket_number = '00'+docket_number
		elif len(docket_number) < 5 or len(docket_number) > 7:
			return ['ERROR', 'Your case number is malformed.']
		year = docket_number[0:2]
		case_id = docket_number[2:7]
		
		query_line = [office + ":" + year + "-" + type_code + "-" + case_id, 
					  court_id]
	else:
		return ['ERROR', 'You are attempting to use a feature that has not'
				'been implemented yet.']
	return query_line

def download_docket_sheet(case_id_query, court_id_query, output_path="."):
# Do we need to add tolerance to the DktReport? (What does this mean?)
	docket_link = ""
	
#!!CYGWIN VS WINDOWS PATH CONVENTIONS
	# Check that the save folder "local_docket_archive" exists
	if not os.path.exists(output_path+"\\results\\"):
		os.makedirs(os.path.abspath(output_path) 
				    + "/results/local_docket_archive")
		print ("Results directory did not exists in the ouput path" 
			  "...folder created.\nLocal Docket Archive directory did not " 
			  "exists in the ouput path...folder created.")
	elif not os.path.exists(output_path+"\\results\local_docket_archive"):
		os.makedirs(os.path.abspath(output_path) 
					+ "/results/local_docket_archive\\")
		print ("Local Docket Archive directory did not exists in the ouput path"
			  "...folder created.")
	
	# Check if this docket has already been downloaded
	docket_path = (output_path + "\\results\\local_docket_archive\\" + 
	            court_id_query + '_' + case_id_query.replace(':', '_').strip()
				+'.html')
	if os.path.exists(docket_path): 
		return [case_id_query, court_id_query, "Docket already downloaded"]
	
	
	#Pull up the search page, and query it
	state = court_id_query[0:2].upper()
	br.open('https://pcl.uscourts.gov/search')
	br.select_form(nr=0)
	try:
		br["case_no"] = case_id_query
	except mechanize._form.ItemNotFoundError as e:
		return [case_id_query, court_id_query, "Could not query case_number."
				"Check that you have logged in."]
	# Optionally, attempt to use the region filter.
	try:
		br["all_region"] = [state]
	except mechanize._form.ItemNotFoundError as e:
		print case_id_query, court_id_query, "Bad Region"
 	br.submit()
	
	source_code=BeautifulSoup(br.response().get_data(), "lxml")

	# Simple error checking
	if "Invalid case number" in source_code.get_text():
		return [case_id_query, court_id_query, "Invalid Case Number"]
	elif "No records found" in source_code.get_text(): 		
		return [case_id_query, court_id_query, "No Search Results"]
	
	# Identify the results table and create a list of search results
	results_table = source_code.find('table', {'align':'center'})	
	if results_table:
		search_results = results_table.findAll('tr')
	else:
		print "ERROR " + case_id_query
		return [case_id_query, court_id_query, "ERROR: No Results Table"]

	# Iterate through the search results to match the court-id and find the 
	# unique result.
	for result in search_results:
		# Skip the column headers
		if not result.find('td', {'class':'court_id'}):
			continue
		# Check to see if the court id matches
		elif court_id_query in result.find('td', {'class':'court_id'}):
			case_name = result.find('td', {'class':'cs_title'}).string
			query_link = result.find('td', {'class':'case'}).a.get('href')
			nos = result.find('td', {'class':'nos'}).string

			# Handle the Dates
			dates= result.find_all('td', {'class':'cs_date'})
			if not dates[0].string: 
				date_filed = "None"
			else: 
				date_filed = dates[0].string
			
			if not dates[1].string: 
				date_closed = "None"
			else: 
				date_closed = dates[1].string
		
			# Convert the query to a direct link to the docket report
			docket_link = result.find('td', {'class':'case'}).a.get('href').replace('iqquerymenu', 'DktRpt')
			detailed_info = [case_id_query, court_id_query, case_name, nos, 
						   date_filed, date_closed, query_link]
			break
			
	# Return if you can't match anything
	if docket_link == "": 
		return [case_id_query, court_id_query, "Unable to match court ID "
		        "in search results"]
		
	# Using the Docket Link, open the relevant dkt-report page
	br.open(docket_link)
	br.select_form(nr = 0)
	br.submit()

	# When you run into the "many docket entries" page
	if "</form>" in br.response().get_data().lower(): 
		br.select_form(nr = 0)
		br.form['date_from'] = ['']
		docket_soup = BeautifulSoup(br.submit().get_data())
	else:
		docket_soup = BeautifulSoup(br.response().get_data())
	
	# Save the docket sheet.
	output_file = codecs.open(docket_path, 'w', encoding='utf-8')
	output_file.write("<!--detailed_info: (\"" + '\",\"'.join(detailed_info) 
					  +"\")-->\n")
	output_file.write(docket_soup.prettify())
	
	# Manually double check
	if case_id_query not in docket_soup.get_text():
		return [case_id_query, court_id_query, 
			    "ERROR: Manually Double Check Downloaded Docket"]

	return [case_id_query, court_id_query, "Docket Downloaded"]


# def download_docket_sheet_from_file():
# Input potential links from a .csv or .tsv file
# Create PACER QUERYs from the .csv
# Initiate a log file
# Attempt to download the dockets
	
def parse_docket(filename):
	parsed_docket_table = []
	
	# Open the .html docket file and parse using BeautifulSoup 
	# into a list of entries
	source = BeautifulSoup(open(filename, 'r'), "lxml")
	for s in source('script'): s.extract()		#Remove Script Elements
	docket_table = source.find('table', {'rules':'all'})
	docket_entries = docket_table.find_all('tr')

	# Parse each entry into a list of characteristics and append to the 
	# parsed_docket_table
	skip_first_line = 0
	for entry in docket_entries:
		if skip_first_line == 0:
			skip_first_line = 1
			continue
		# Turn the docket entry into a list		
		row_cells = entry.find_all('td')
		row_contents = [cell.get_text(' ', strip=True) for cell in row_cells]
		
		# Replace missing information
		if row_contents[0] == '':row_contents[0]='NA'
		if row_contents[1] == '':row_contents[1]='NA'
		
		# Search for the link to a document
		link = row_cells[1].find('a')
		if link:
			link_exist = '1'
			link = link.get('href')
		else:
			link_exist = '0'
			link = ''
			
		row_contents.append(link_exist)
		row_contents.append(link)
		parsed_docket_table.append(row_contents)

	return parsed_docket_table


def parse_docket_dir(directory, 
					 regex_filename_format="(?P<court_id>\w\w\w\w\w\w)_"
					 "(?P<office>\d)_(?P<year>\d\d)\-(?P<type>\w\w)\-"
					 "(?P<case_id>\d\d\d\d\d)\.html", 
					 output_file='./results/parsed_local_docket_archive.dump'):
	
	# INITALIZATION
	list_of_files = []
	case_dictionary = {}

	# Identify search for all .html files in the directory and
	# add them to a list
	for root, dirs, files in os.walk(directory):
		for file in files:
			path = directory+file
			if re.search('\.html', file):
				list_of_files.append([file,path])
	
	# For each docket, create a unique key, parse it and add to case dictionary
	for file in list_of_files:
		parsed_filename = re.search(regex_filename_format, file[0])
		
		# Check if the file is in the specified format
		if not parsed_filename:
			print "Error in file ", file
			continue	
		
		# Create a unique key
		file_key = (parsed_filename.group('court_id'), 
					parsed_filename.group('office'), 
					parsed_filename.group('year'), 
					parsed_filename.group('type'), 
					parsed_filename.group('case_id'))
		
		case_dictionary[file_key] = parse_docket(file[1])
	
	# Write the case_dictionary to an output file
	with open(output_file, 'w') as f: pickle.dump(case_dictionary, f, 2)
	f.close()
	
	return case_dictionary
	
	
def copy_docket(filename, save_directory):
	source_file=open(local_docket_archive+filename+".html", 'r')
	output_file=open(save_directory+filename+".html", 'w+')
	output_file.write(source_file.read())
	output_file.close()
	source_file.close()
#	print str(filename)+"...resaved to" + str(save_directory)
	return

	
def download_document(key, dictionary, output_path='.'):
# Check the try/except statement (too includive error-handling?)
# Needs to be modified so that we can get the correct individual website, 
# e.g. NYSDCE --> NYSD; the .replace('ce', '') is hardcoded right now
	# Initialize Filename and Save Directory
	identifier=key[1]+':'+key[2]+'-'+key[3]+'-'+key[4]
	filename=(key[0]+'_'+key[1]+'_'+key[2]+'-'+key[3]+'-'+key[4]+"_document_"+
			 dictionary[key][1]+".pdf")
	save_directory=output_path + "/results/local_document_archive/"
	
	# Check that the download folder exists
	if not os.path.exists(output_path+"\\results\\"):
		os.makedirs(os.path.abspath(output_path) + 
					"/results/local_document_archive")
		print ("Results directory did not exists in the ouput path...folder "
			  "created.\nLocal Docket Archive directory did not exists in the "
			  "ouput path...folder created.")
	elif not os.path.exists(output_path+"\\results\local_document_archive"):
		os.makedirs(os.path.abspath(output_path) + 
					"/results/local_document_archive")
		print ("Local Docket Archive directory did not exists in the ouput "
			  "path...folder created.")
	
	# Check if you've downloaded this document before:
	if os.path.exists(save_directory+filename):
		return [identifier, key[0], dictionary[key][1],
				"Document Already Downloaded"]

	# Check if there is a link, and then create the full hyperlink
	if dictionary[key][3] == '1':
		document_link = ("https://ecf."+key[0].replace('ce', '')+
						 ".uscourts.gov"+dictionary[key][4])
	else:
		return [identifier, key[0], dictionary[key][1], "No Download Link"]

	# Assemble and encode POST information from the hyperlink
	case_id = re.search('caseid=(?P<caseid>\d*)', dictionary[key][4])
	if case_id:
		case_id = case_id.group('caseid')
	else: 
		return [identifier, key[0], dictionary[key][1], 
				"BAD POST:Could not find case_id"]
		
	de_seq_num = re.search('de_seq_num=(?P<de_seq_num>\d*)', 
							dictionary[key][4])
	if de_seq_num:
		de_seq_num = de_seq_num.group('de_seq_num')
	else: 
		return [identifier, key[0], dictionary[key][1], 
				"BAD POST: Could not find de_seq_num"]
	
	post_parameters = {'caseid':case_id, 
					   'de_seq_num':de_seq_num, 
					   'got_receipt':'1', 
					   'pdf_header':'2', 
					   'pdf_toggle_possible':'1'}
	post_data=urllib.urlencode(post_parameters)
# DO WE NEED THIS TRY? MAYBE SOME OTHER SORT OF MAX_ATTEMPTS KIND OF THING?
# WHAT ERROR IS BEING THROWN HERE?	
	# Open the document link (which will bring you to a charge page).
	try:
		temp_soup=BeautifulSoup(br.open(document_link))
	except:
		return [identifier, key[0], dictionary[key][1], "BAD LINK: Could not "
				"open URL"]

	# Is there a form on the page? 
	viewdoc_url=temp_soup.find('form', {'action':True})

	# If no, then we have entered into a multi-document query. 
	# Find the first document link. 
	if not viewdoc_url:
		#Find the first document's link.
		multipage_viewdoc_url = temp_soup.find('a', {'onclick':True})
		#Follow the first document's link
		temp_soup = BeautifulSoup(br.open(multipage_viewdoc_url.get('href')))
		#We should not be at the "Accept Charges Page"
		viewdoc_url = temp_soup.find('form', {'action':True})

	#Get the final link to the document and request it by encoding post_data.
	document_url = viewdoc_url.get('action')
	document = br.open(document_url, post_data)

	#The PDF should be embedded in an iframe. 
	iframes_src = re.search("/cgi-bin/show_temp\.pl\?file=.*=application/pdf", 
							document.get_data())
	
	#Sometimes, it is not. Then, directly write it.
	if not iframes_src:
		#Save the document
		with open(save_directory+filename, 'w') as output_file: 
			output_file.write(document.get_data())
		output_file.close()
		return [identifier, key[0], dictionary[key][1], 
				"Document Downloaded, no iframes"]
	
	#Follow the iframes link 
	document=br.open("https://ecf."+key[0].replace('ce', '')+".uscourts.gov"+
					 iframes_src.group(), post_data)
	with open(save_directory+filename, 'w') as output_file: 
		output_file.write(document.get_data())
	output_file.close()
	
	return [identifier, key[0], dictionary[key][1], 
			"Document Downloaded, iframes"]
