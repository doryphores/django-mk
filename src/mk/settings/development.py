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