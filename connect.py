from google.cloud import datastore
from google.oauth2 import service_account
import pymysql
import os

# This file will return the connection needed to hook up with Cloud SQL and Datastore.
# Hosted on app engine, uncomment below code to connect local machine.

def sql_connect():
    #Define connection based on operating system. Values defined in app.yaml file
    #   Method is called in main.py file for any SQL connections that need to be made

    db_user = os.environ.get('SQL_USER')
    db_password = os.environ.get('SQL_PASSWORD')
    db_name = os.environ.get('SQL_DATABASE')
    db_connection_name = os.environ.get('INSTANCE_CONNECTION_NAME')
    unix_socket = '/cloudsql/{}'.format(db_connection_name)

    #if os.environ.get('GAE-ENV') == 'standard':  # means configured to App Engine
    conn = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name, autocommit=True)
    #else:  # Connection is local machine. Use proxy.
     #   host = '127.0.0.1'
      #  conn = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name, autocommit=True)
    return conn


def ds_connect():
    #if os.environ.get('GAE-ENV') == 'standard':  # means configured to App Engine
    client = datastore.Client()
    #else:
     #   safile = "service-bq.json"
      #  credentials = service_account.Credentials.from_service_account_file(safile)
       # client = datastore.Client(project='cpb100-213205', credentials=credentials)
    return client
