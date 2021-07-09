filename = r'C:\Users\44797\Downloads\PokerStars Tracker UK Wave 100_21070606.csv'

import csv
import pyodbc

with open(filename,encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    headers = next(reader)
    reader = list(reader)

    connection = pyodbc.connect('Driver={SQL Server};'
					        'Server=.\sqlexpress;'
					        'Database=Pokerstars;'
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
	    		SQL_insert_query = """INSERT INTO pokerstars (Data) VALUES ('%s') """ % s

	    		cursor = connection.cursor()
	    		cursor.execute(SQL_insert_query)
	    		connection.commit()
	    		print(cursor.rowcount, "Record inserted successfully into table")
	    		cursor.close()

	    	except pyodbc.Error as error:
	    		print("Failed to insert record into table {}".format(error))

    except IndexError as error:
	    print('No more rows left to insert')
