README
This is intended to faciliate downloading both dockets and case documents from 
the PACER database. The PACER database is a pay-for-use database, so it will 
require that you already have an associated PACER account.

FUNCTIONS REFERENCE
login_to_pacer(username, password)
	-- Before specifying your queries, you must login to your PACER account using 
	your username and password.
	
create_PACER_query(district, office, docket_number, type_code)
	-- Create a PACER query from case attributes. 
	-- Returns a two item list,  [case_id_query, court_id_query]
	
	`district' 		--> Either a 3 or 4 character district/state code (e.g., 
						Eastern	District of New York is abbreviated as 'EDNY' or
						'ED NY') or full text name of the district (e.g., 
						'Eastern District of New York')
	`office' 		-->  An integer or string denoting the office number.
	`docket_number' --> An integer or string that captures the year and case 
						 number.
	`type_code' 	--> "civil", "criminal", "bankruptcy"

download_docket_sheet(case_id_query, court_id_query, output_path="."):
	-- Downloads a specifc docket sheet from PACER and stores it to 
		'.\results\local_docket_archive\'
	-- Returns a list, [case_id_query, court_id_query, STATUS), where STATUS
		is a string indicating success or any errors that occured during
		downloading.
	-- Write some detailed info as an HTML comment at the beginning of the saved
		file.
	`case_id_query'	--> A case query in the format specified by PACER, i.e. 
						office_number:year-case_number. You can use
						create_PACER_query to properly format your case 
						attributes.
	`court_id_query'--> The PACER identification of a court (e.g., nyedce). You 
						can use create_PACER_query to properly format your court 
						identifier.
	`output_path'	--> The path to your `results' folder. Defaults to the 
						script directory. If a 'results' folder does not exist, 
						it will be created for you.
	
parse_docket(filename)
	-- Returns a list, where each element corresponds to a docket entry and 
		where each docket entry is a list formatted as,
		[date filed, entry number, entry description, indicator for link 
		existence, link (if it exists) to the entry's document]
		
parse_docket_dir(directory, 
				 regex_filename_format="(?P<court_id>\w\w\w\w\w\w)_"
					"(?P<office>\d)_(?P<year>\d\d)\-(?P<type>\w\w)\-"
					 "(?P<case_id>\d\d\d\d\d)\.html", 
				 output_file='./results/parsed_local_docket_archive.dump')
	-- Parses all the files in a directory that have a filename that matches the
		regex specification (court_id, office, case_id) and stores the parsed
		docket to a dictionary that is written to a PICKLE file.
		archive.
	-- Each docket is assigned a key that is a tuple,
		(court_id, office, year, type, case_id). This key identifies the docket
		in the dictionary. The value of the key is the list of lists returned by
		parse_docket.

	`directory'		--> Path to the the directory containing your dockets.
						Dockets must bein .html format.
	`regex_filename_format' --> Defaults to the format that 
								download_docket_sheet uses.
	`output_file'	--> Specifies the PICKLE file. Defaults to 
						`parsed_local_docket_archive.dump'

					 
download_document(key, dictionary, output_path='.')
	--Downloads a specific document associated with a docket entry.

	`key'			--> A tuple, (court_id, office, year, type, case_id), that
						identifies the case.
	`dictionary'	--> The dictionary which associate the key with the specific
						docket entry ([date filed, entry number, description, 
						link existence, link]) which is to be downloaded.
	`output_path'	--> Where you would like the file to be saved. Defaults to 
						the directory of the script.

