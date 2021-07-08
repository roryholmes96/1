file1 = r'C:\Users\44797\Downloads\PokerStars Tracker UK Wave 100_21070606.csv'
file2 = r'C:\Users\44797\OneDrive\Documents\pokerstars.csv'

import csv
import pyodbc

with open(file1) as f:
    reader = csv.reader(f)
    headers = next(reader)
    reader = list(reader)

    connection = pyodbc.connect('Driver={SQL Server};'
					        'Server=.\sqlexpress;'
					        'Database= xxxxx;'
					        'Trusted_connection=yes')

    try:
	    for i in range(9999999999999999999999):
	    	a=list(zip(headers, reader[i]))
	    	s = ''
	    	field = 1
	    	for x,y in a:
	    		if field == 1:
	    			s+=(f'{x}={y}')
	    			field +=1
	    		else:
	    			s+=(f'&{x}={y}')
	    	try:
	    		SQL_insert_query = """INSERT INTO xxxxx (xxxxx) VALUES ('%s') """ % s

	    		cursor = connection.cursor()
	    		cursor.execute(SQL_insert_query)
	    		connection.commit()
	    		print(cursor.rowcount, "Record inserted successfully into table")
	    		cursor.close()

	    	except pyodbc.Error as error:
	    		print("Failed to insert record into table {}".format(error))
	except IndexError as error:
		print('No more rows left to insert')
