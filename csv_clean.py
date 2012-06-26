import csv

csv.register_dialect("motoactv", delimiter = ",", quoting = csv.QUOTE_ALL)

LON = 'LONGITUDE'
LAT = 'LATITUDE'

MIN_LON = 1e-1
MIN_LAT = 1e-1

STATE_ZERO = 1
STATE_DATA = 2

def csv_cleanup(infile, outfile):
	dictReader = csv.DictReader(infile, dialect="motoactv")
	rows = []
	for row in dictReader:
		rows += [row]
	
	prev_state = STATE_DATA
	last_idx = None
	for i in range(len(rows)):
		curr_state = STATE_ZERO if (abs(float(rows[i][LON])) < MIN_LON or abs(float(rows[i][LAT])) < MIN_LAT) else STATE_DATA
		
		# action on transition STATE_ZERO -> STATE_DATA 
		if prev_state == STATE_ZERO and curr_state == STATE_DATA:
			# zeros at start of data
			if last_idx == None:
				for j in range(i):
					rows[j][LON] = rows[i][LON]
					rows[j][LAT] = rows[i][LAT]
			else:
				delta_d = {}
				delta_d[LON] = float(rows[i][LON]) - float(rows[last_idx][LON])
				delta_d[LAT] = float(rows[i][LAT]) - float(rows[last_idx][LAT])
				delta_t = i - last_idx
				start_idx = last_idx + 1
				for j in range(start_idx, i):
					rows[j][LON] = float(rows[last_idx][LON]) + (j-start_idx+1) * delta_d[LON] / delta_t
					rows[j][LAT] = float(rows[last_idx][LAT]) + (j-start_idx+1) * delta_d[LAT] / delta_t

		# store last idx for STATE_DATA
		if curr_state == STATE_DATA:
			last_idx = i
			
		prev_state = curr_state
	
	# zeros at end of data and data not all zeros
	if prev_state == STATE_ZERO and last_idx != None:
		for j in range(last_idx, len(rows)):
			rows[j][LON] = rows[last_idx][LON]
			rows[j][LAT] = rows[last_idx][LAT]
	
	dictWriter = csv.DictWriter(outfile, dictReader.fieldnames, dialect="motoactv")
	dictWriter.writeheader()
	dictWriter.writerows(rows)

with open("rawDataCsv.csv", "rb") as infile:
	with open('rawDataCsvClean.csv', 'wb') as outfile:
		csv_cleanup(infile, outfile)
	