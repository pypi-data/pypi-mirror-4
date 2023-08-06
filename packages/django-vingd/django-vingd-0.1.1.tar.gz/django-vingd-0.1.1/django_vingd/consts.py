from django.conf import settings

VINGD_MODE = getattr(settings, 'VINGD_MODE', 'production')
VINGD_SETTINGS = settings.VINGD_SETTINGS[VINGD_MODE]

SETTINGS = {
    'production': {
        'VINGD_FRONTEND': 'https://www.vingd.com',
        'VINGD_BACKEND': 'https://api.vingd.com/broker/v1/',
        'VINGD_CDN': 'https://apps.vingd.com/cdn/',
    },
    'sandbox': {
        'VINGD_FRONTEND': 'http://www.sandbox.vingd.com',
        'VINGD_BACKEND': 'https://api.vingd.com/sandbox/broker/v1/',
        'VINGD_CDN': 'https://apps.vingd.com/cdn/',
    }
}.get(VINGD_MODE) or {}

SETTINGS.update(VINGD_SETTINGS)

VINGD_FRONTEND = SETTINGS['VINGD_FRONTEND']
VINGD_BACKEND = SETTINGS['VINGD_BACKEND']
VINGD_CDN = SETTINGS['VINGD_CDN']
VINGD_USR = SETTINGS['VINGD_USR']
VINGD_PWD = SETTINGS['VINGD_PWD']
