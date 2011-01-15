from mk.settings.development import *

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

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