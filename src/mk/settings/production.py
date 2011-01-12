from mk.settings.base import *

BASE_URL = 'http://192.168.1.134'

ADMIN_MEDIA_PREFIX = '/static/admin-media/'

DATABASES['import'] = {
    'ENGINE': 'sql_server.pyodbc',
    'NAME': 'kartleague',
    'HOST': r'192.168.1.182\SQLEXPRESS',
    'USER': 'sqlogin',
    'PASSWORD': 'd1lb3rt',
    'OPTIONS': {
        'driver': 'FreeTDS',
        'host_is_server': True,
    },
}