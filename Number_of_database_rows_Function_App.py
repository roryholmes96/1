import logging
import azure.functions as func
import pyodbc

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    table = req.params.get('table')

    if table:

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
        cursor.execute(f'SELECT COUNT(*) FROM {table}')

        numberOfRows = ''
        for row in cursor:
            for field in row:
                numberOfRows += str(field)

        return func.HttpResponse(f'{numberOfRows}')
    else:
        return func.HttpResponse(
             'This HTTP triggered function executed successfully. Pass a table'\
             'in the query string to receive the number of rows.',
             status_code=200
        )
