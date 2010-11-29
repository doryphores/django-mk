from mk.settings.base import *

DEBUG = True

BASE_URL = 'http://192.168.1.70/mk'

DATABASES['import'] = {
    'ENGINE': 'sql_server.pyodbc',
    'NAME': 'kartleague',
    'USER': 'sqlogin',
    'PASSWORD': 'd1lb3rt',
    'OPTIONS': {
        'dsn': 'ADAM_MSSQL',
    },
}