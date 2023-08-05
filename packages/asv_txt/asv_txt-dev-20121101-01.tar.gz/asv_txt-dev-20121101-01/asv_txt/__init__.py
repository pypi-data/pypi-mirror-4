import os

__name__ = 'asv_txt'
__version__ = 'dev-20121101-01'
__keywords__ = 'django asv TextField'
__description__ = '''
This module helps you for attaching text fields
to any django models trought ContentType.
In this fields You may use Creole wiki markup and some 
additional macroses, as <<img NNN>> <<yt key>>
'''

if os.getenv('DJANGO_SETTINGS_MODULE'): 
    from asv_txt.settings import Settings
    settings = Settings()
#
