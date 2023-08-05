from settings.defaults import *


EUKALYPSE_BROWSER='chrome'
EUKALYPSE_HOST='http://192.188.23.18:4444'

EMAIL_HOST = 'mail.s-v.de'

#SENTRY_DSN = 'http://10eb8cf305f741e9acf227a82f12d21a:017e859ff4434ae496b001f5d1f638de@sentry.inhouse.s-v.de:9000/12'

if SENTRY_DSN:
    LOGGING['handlers']['sentry'] ={
            'level': 'INFO',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        }
    LOGGING['loggers']['django.request']['handlers'].append('sentry')
