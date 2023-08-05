
from indivo_client_py import IndivoClient

import settings

from hashlib import md5

def get_indivo_client(request, with_session_token=True, token=None):
    server_params = {"api_base": settings.INDIVO_SERVER_LOCATION,
                     "authorization_base": settings.INDIVO_UI_SERVER_BASE}
    consumer_params = settings.INDIVO_SERVER_OAUTH
    if with_session_token:
        token = request.session['access_token']
    client = IndivoClient(server_params, consumer_params, resource_token=token)
    return client

def _sessionkey(record_id=None, carenet_id=None):
    """
        Use the record_id or the carenet_id to create a unique session key.
    """
    if record_id:
        key = "%s:%s" % (settings.SUBMODULE_NAME, record_id)
    else:
        key = "%s:%s" % (settings.SUBMODULE_NAME, carenet_id)
    key = md5(key).hexdigest()[:8]
    return key
