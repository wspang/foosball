from google.cloud import bigquery
from google.oauth2 import service_account
import pymysql
import os
# This file will return the connection needed to hook up with Cloud SQL

"""def sql_connect():
    #Define connection based on operating system. Values defined in app.yaml file
    #   Method is called in main.py file for any SQL connections that need to be made

    db_user = os.environ.get('SQL_USER')
    db_password = os.environ.get('SQL_PASSWORD')
    db_name = os.environ.get('SQL_DATABASE')
    db_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')

    if os.environ.get('GAE-ENV') == 'standard':  # means configured to App Engine
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        conn = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
    else:  # Connection is local machine. Use proxy.
        host = '127.0.0.1'
        conn = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)
    return conn"""

def bq_connect():
    safile = "service-bq.json"
    credentials = service_account.Credentials.from_service_account_file(safile)
    client = bigquery.Client(project='cpb100-213205', credentials=credentials)
    return client
