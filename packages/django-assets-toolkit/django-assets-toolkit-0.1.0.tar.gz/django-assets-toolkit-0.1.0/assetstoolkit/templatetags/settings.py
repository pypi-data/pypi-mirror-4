from django.conf import settings


STATIC_URL = settings.STATIC_URL
STATIC_ROOT = getattr(settings, 'STATIC_ROOT', getattr(settings, 'MEDIA_ROOT'))
LOAD_PATHS = getattr(settings, 'SCSS_LOAD_PATHS', settings.STATICFILES_DIRS)
ASSETS_ROOT = getattr(settings, 'SCSS_ASSETS_ROOT', settings.MEDIA_ROOT + 'assets/')
ASSETS_URL = getattr(settings, 'SCSS_ASSETS_URL', settings.MEDIA_URL + 'assets/')
SCSS_COMPRESS = getattr(settings, 'SCSS_COMPRESS', True)
SCSS_DEBUG_INFO = getattr(settings, 'SCSS_DEBUG_INFO', True)
SCSS_REBUILD = getattr(settings, 'SCSS_REBUILD', True)
COFFEE_OUTPUT = getattr(settings, 'COFFEE_OUTPUT', 'js')
COFFEE_REBUILD = getattr(settings, 'COFFEE_REBUILD', True)
