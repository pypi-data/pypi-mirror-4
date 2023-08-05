from logan.runner import run_app



CONFIG_TEMPLATE = """
import os.path

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(CONF_ROOT, 'eukalypse_now.db'),
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Mail server configuration

# For more information check Django's documentation:
#  https://docs.djangoproject.com/en/1.3/topics/email/?from=olddocs#e-mail-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False


SITE_URL = 'http://localhost:8000'
MEDIA_URL = SITE_URL + '/media/'
MEDIA_ROOT=''

SENTRY_DSN = ''

if SENTRY_DSN:
    LOGGING['handlers']['sentry'] ={
            'level': 'INFO',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        }
    LOGGING['loggers']['django.request']['handlers'].append('sentry')

"""


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """
    return CONFIG_TEMPLATE


def main():
    run_app(
        project='eukalypse_now',
        default_config_path='~/.eukalypse_now/eukalypse_now.conf.py',
        default_settings='eukalypse_now.settings.defaults',
        settings_initializer=generate_settings,
        settings_envvar='EUKALYPSE_NOW_CONF',
    )

if __name__ == '__main__':
    main()
