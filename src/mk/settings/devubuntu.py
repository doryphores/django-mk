from mk.settings.development import *

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