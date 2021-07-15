'''Sends a bunch of parallel HTTP requests to function App. Function App gets 
some part of data from SQL, converts it to CSV format and returns this as a
string. This program retrieves the strings in parallel and then writes them to 
a CSV file.'''

#Modifiable Inputs
numberOfThreads = 3
headersFile = 'pokerstars_headers.csv'
newFile = 'pokerstars_data.csv'
table = 'pokerstars'

import pyodbc, csv, requests, json
from requests_futures.sessions import FuturesSession
import time
from datetime import timedelta
start_time = time.monotonic()

def writeToFile(resp, *args, **kwargs):
	'''writes responses to file in order the requests are finished'''
	end_time = time.monotonic()
	print(timedelta(seconds=end_time - start_time))
	print(resp)
	# newFile.write(resp.text.replace('\n',''))

#Creates a list of headers from CSV file containing headers
#then converts this list to JSON.
with open(headersFile, encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    headers = next(reader)

jsonHeaders = json.dumps(headers)

##Opens the file which the CSV data will be written to.
# newFile = open(newFile,'a')

#Sends a request to a function app which returns the number of database rows
numberOfRowsRequest = requests.get(\
	f'https://sql-to-csv.azurewebsites.net/api/HttpTrigger_Get_Number_of_Database_Rows?table={table}')

numberOfRows = int(numberOfRowsRequest.text)

#Creates list of batches based on number of rows
rowBatches=[]
for i in range(numberOfThreads):
	lower = (numberOfRows//numberOfThreads)*(i)+1
	if i+1 == numberOfThreads:
		upper = numberOfRows
	else:
		upper = (numberOfRows//numberOfThreads)*(i+1)
	rowBatches.append((lower, upper))

#Creates a future for each rowBatch.
# "session.hooks['response']" assigns the responses for these futures to the 
# writeToFile functionv in the order that they are recieved.
session = FuturesSession()
session.hooks['response'] = writeToFile

for rowBatch in rowBatches:
	params = {'table': table, 'firstRow':rowBatch[0], 'lastRow':rowBatch[1]}
	future = session.get(\
		'https://sql-to-csv.azurewebsites.net/api/HttpTrigger_SQL_to_CSV',\
		data=jsonHeaders, params=params)

##Writes headers into new file whilst requests are being completed
# writer = csv.DictWriter(newFile, fieldnames=headers)
# writer.writeheader()
