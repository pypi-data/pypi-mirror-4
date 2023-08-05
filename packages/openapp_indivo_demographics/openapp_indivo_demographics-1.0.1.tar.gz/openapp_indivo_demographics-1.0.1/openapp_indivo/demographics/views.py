
""" 
Kevin Gill kevin.gill@openapp.ie


"""

import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.exceptions import NON_FIELD_ERRORS


from utils import get_indivo_client, _sessionkey
import forms
import models

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------
# These requests support the authentication protocol.
# Authorisation is given for a specific App in the context of either
# a record or a carenet.
#
# These calls are used to set up some data in the session object to
# be used to authorise requests to the server. The approach is generic
# and could be moved to a non-app specific location

def _loggedIn(request, record_id=None, carenet_id=None):
    session_key = _sessionkey(record_id=record_id, carenet_id=carenet_id)
    if request.session.get(session_key):
        return True
    return False


def start_auth(request):
    """
    begin the oAuth protocol with the server
    
    expects either a record_id or carenet_id parameter,
    now that we are carenet-aware
    """
    
    # do we have a record_id?
    record_id = request.GET.get('record_id', None)
    carenet_id = request.GET.get('carenet_id', None)

    if _loggedIn(request, record_id, carenet_id):
        sessionkey = _sessionkey(record_id=record_id, carenet_id=carenet_id)
        url = "%s/demographics" % sessionkey
        return HttpResponseRedirect(url)

    # create the client to Indivo
    client = get_indivo_client(request, with_session_token=False)
    
    # prepare request token parameters
    params = {'oauth_callback':'oob'}
    if record_id:
        params['indivo_record_id'] = record_id
    if carenet_id:
        params['indivo_carenet_id'] = carenet_id
    
    # request a request token
    req_token = client.fetch_request_token(params)

    # store the request token in the session for when we return from auth
    request.session['request_token'] = req_token
    
    # redirect to the UI server
    return HttpResponseRedirect(client.auth_redirect_url)

def after_auth(request):
    """
    after Indivo authorization, exchange the request token for an access token and store it in the web session.
    """
    # get the token and verifier from the URL parameters
    oauth_token, oauth_verifier = request.GET['oauth_token'], request.GET['oauth_verifier']
    
    # retrieve request token stored in the session
    token_in_session = request.session['request_token']
    
    # is this the right token?
    if token_in_session['oauth_token'] != oauth_token:
        return HttpResponse("oh oh bad token")
    
    # get the indivo client and use the request token as the token for the exchange
    client = get_indivo_client(request, with_session_token=False)
    client.update_token(token_in_session)
    access_token = client.exchange_token(oauth_verifier)
    
    record_id = carenet_id = None
    
    if access_token.has_key('xoauth_indivo_record_id'):
        record_id = access_token['xoauth_indivo_record_id']
    else:
        carenet_id = access_token['xoauth_indivo_carenet_id']
    
    # store stuff in the session
    session = dict()
    session['access_token'] = access_token
    session['carenet_id'] = carenet_id
    session['record_id'] = record_id
    sessionkey = _sessionkey(record_id=record_id, carenet_id=carenet_id)
    request.session[sessionkey] = session
    url = "%s/demographics" % sessionkey
    return HttpResponseRedirect(url)

#------------------------------------------------------------------------
# These are the views for the application. For the moment there are only
# two, display and edit.

# Demographics data can only be edited by the owner of the record. The
# edit function is only available to record owners. Carenet members cannot
# edit the demographics document.

def demographics(request, sessionkey):

    session = request.session.get(sessionkey)
    record_id = session.get('record_id', None)
    if record_id:
        data = models.Demographics.objects.get(record_id=record_id)
    else:
        carenet_id = session.get('carenet_id', None)
        data = models.Demographics.objects.get(carenet_id=carenet_id)

    return render_to_response("openapp_indivo/demographics/demographics.html", {'demographics': data},
        context_instance=RequestContext(request))


def edit(request, sessionkey):
    session = request.session.get(sessionkey)
    record_id = session.get('record_id', None)
    if not record_id:
        carenet_id = session.get('carenet_id', None)
    else:
        carenet_id = None

    if record_id:
        data = models.Demographics.objects.get(record_id=record_id)
    else:
        data = models.Demographics.objects.get(carenet_id=carenet_id)

    if request.method == 'POST':
        form = forms.DemographicsForm(request.POST, instance=data)
        if form.is_valid(): 
            try:
                if form.has_changed():
                        form.save()
                return HttpResponseRedirect('demographics') 
            except Exception, e:
                logger.exception("Error saving record to Indivo Server")
                form.errors[NON_FIELD_ERRORS] = str(e)
    else:
        form = forms.DemographicsForm(model_to_dict(data)) # An unbound form

    # TODO: Messages
    return render(request, 'openapp_indivo/demographics/edit.html', {'form': form})
