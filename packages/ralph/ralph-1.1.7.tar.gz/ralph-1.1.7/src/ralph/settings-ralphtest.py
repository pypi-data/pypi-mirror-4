#
# A testing profile. 
#
execfile('/Users/ambv/.ralph/settings')
SECRET_KEY = 'Ralph--remember what we came for. The fire. My specs.'
DEBUG = False
TEMPLATE_DEBUG = False
DUMMY_SEND_MAIL = False
SEND_BROKEN_LINK_EMAILS = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {},
    }
}
LOGGING['handlers']['file']['filename'] = CURRENT_DIR + 'runtime.log'
BROKER_HOST = "localhost"
BROKER_PORT = 25672
BROKER_USER = "ralph"
BROKER_PASSWORD = "ralph"
BROKER_VHOST = "/ralph"
