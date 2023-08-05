from django.conf import settings # top-level setttings

SUBMODULE_NAME = 'demographics'
INDIVO_SERVER_OAUTH = {
  'consumer_key': SUBMODULE_NAME+'@apps.openapp.ie',
  'consumer_secret': SUBMODULE_NAME
}
INDIVO_SERVER_LOCATION = settings.INDIVO_SERVER_LOCATION
INDIVO_UI_SERVER_BASE = settings.INDIVO_UI_SERVER_BASE

