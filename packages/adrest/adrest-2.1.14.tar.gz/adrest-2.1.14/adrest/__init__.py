version_info = (2, 1, 14)

__version__ = version = '.'.join(map(str, version_info))
__project__ = PROJECT = __name__
__author__ = AUTHOR = "Kirill Klenov <horneds@gmail.com>"
__license__ = LICENSE = "GNU LGPL"

try:
    from django.conf import settings as django_settings # nolint
    if django_settings.configured \
       and not 'adrest' in django_settings.INSTALLED_APPS:
        import logging
        logging.warn('You should add "adrest" to INSTALLED_APPS.')
except ImportError:
    pass
