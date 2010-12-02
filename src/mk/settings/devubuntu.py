from mk.settings.development import *

DATABASES['import'] = {
	'ENGINE': 'sql_server.pyodbc',
	'NAME': 'kartleague',
	'USER': 'sqlogin',
	'PASSWORD': 'd1lb3rt',
	'OPTIONS': {
		'dsn': 'ADAM_MSSQL',
	},
 }
