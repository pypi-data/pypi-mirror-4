import os

__name__ = 'asv_imgs'
__version__ = 'dev-20121101-01'
__keywords__ = 'django asv images'
__description__ = '''
Module for connecting images to articles and other django models trought ContentTypes.
'''

if os.getenv('DJANGO_SETTINGS_MODULE'):
    from asv_imgs.settings import Settings
    settings = Settings()
#
