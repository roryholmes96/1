import logging
import azure.functions as func
import pyodbc, io, csv, json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python SQL to CSV HTTP trigger function processed a request.')

    table = req.params.get('table')
    firstRow = req.params.get('firstRow')
    lastRow = req.params.get('lastRow')
    jsonHeaders= req.get_body()

    if table and firstRow and lastRow and jsonHeaders:
        logging.info(f'Recieved jsonHeaders and parameters firstRow:'\
                     f'{firstRow}, lastRow:{lastRow}.')

        headers = json.loads(jsonHeaders)

        connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};\
                                    Server=r96-server.database.windows.net,1433;\
                                    Database=r96_database;\
                                    Uid=rory;\
                                    Pwd=Omnisis1;\
                                    Encrypt=yes;\
                                    TrustServerCertificate=no;\
                                    Connection Timeout=30')

        logging.info(f'Connected to database and retrieving data.')

        cursor = connection.cursor()
        cursor.execute(f'SELECT Data\
                         FROM {table}\
                         WHERE ID\
                         BETWEEN {firstRow} AND {lastRow}')

        data = []
        for row in cursor:
            data.append(f'{row[0]}')
        
        connection.close()

        logging.info(f'Data retrieved. Disconected from database.')

        rows = []
        for row in data:
            row = row.split('&')
            row[:] = [i.split('=') for i in row]
            row = dict(row)
            rows.append(row)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        for row in rows:
            writer.writerow(row)

        logging.info(f'Data converted to CSV format and being returned.')

        return func.HttpResponse(output.getvalue())

    else:
        return func.HttpResponse(
             'This HTTP triggered function executed successfully. To return SQL'\
             'data send a JSON list of headers in the request body, and input'\
             'the table, firstRow and lastRow values into the query string.',
             status_code=200
        )
