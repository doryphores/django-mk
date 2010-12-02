from mk.settings.base import * 

DEBUG = True

INSTALLED_APPS += (
	'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
	'INTERCEPT_REDIRECTS': False,
}

DATABASES['import'] = {
	'ENGINE': 'sqlserver_ado',
	'NAME': 'kartleague',
	'USER': 'sqlogin',
	'PASSWORD': 'd1lb3rt',
	'HOST': r'192.168.1.182\SQLEXPRESS',
	'OPTIONS': {
		'provider': 'SQLOLEDB',
		'use_mars': True,
	},
}