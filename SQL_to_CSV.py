import pyodbc, csv
 
headersFile = 'pokerstars_headers.csv'
newFile = 'pokerstars_data.csv'

with open(headersFile,encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    fieldnames = next(reader)

connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};\
                             Server=r96-server.database.windows.net,1433;\
                             Database=r96_database;\
                             Uid=rory;\
                             Pwd=Omnisis1;\
                             Encrypt=yes;\
                             TrustServerCertificate=no;\
                             Connection Timeout=30')

cursor = connection.cursor()
cursor.execute('SELECT Data FROM r96_database.dbo.pokerstars')

data = []
for row in cursor:
    data.append(f'{row[0]}')

rows = []
for row in data:
    row = row.split('&')
    row[:] = [i.split('=') for i in row]
    row = dict(row)
    rows.append(row)

with open(newFile, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
