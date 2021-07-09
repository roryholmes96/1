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

cursor = connection.cursor()

try:
    for i in range(9999999999999999999999):
    	varResPairs=list(zip(headers, reader[i]))
    	rowString = ''
    	field = 1
    	for variable, response in varResPairs:
    		if field == 1:
    			rowString+=(f'{variable}={response}')
    			field +=1
    		else:
    			rowString+=(f'&{variable}={response}')

    	try:
    		SQL_insert_query = """INSERT INTO pokerstars (Data) VALUES ('%s') """ % rowString

    		cursor.execute(SQL_insert_query)
    		connection.commit()
    		print(cursor.rowcount, "Row inserted successfully into table")

    	except pyodbc.Error as error:
    		print("Failed to insert row into table {}".format(error))

except IndexError as error:
    print('No more rows left to insert')

cursor.close()
connection.close()
