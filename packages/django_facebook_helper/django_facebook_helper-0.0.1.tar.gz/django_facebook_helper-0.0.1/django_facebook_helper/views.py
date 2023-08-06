# Create your views here.

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError


import urllib
import cgi
import json
import facebook
import time
import datetime
from django.contrib import auth

import logging
from facebook import parse_signed_request, get_access_token_from_code, auth_url
logger = logging.getLogger(__name__)



FACEBOOK_APP_ID = "226504147430937"
FACEBOOK_APP_SECRET = "cc2b984e2a8726a6e7c45371e7c257ee"
REDIRECT_URL = "http://local.filmsobsession.com:8000/facebook-redirect/"


"""
friends = graph.get_connections("me", "friends")
params["friends"] = friends

params["get"] = request.GET

print params

graph.put_object("me", "feed", message="Hello, world")
""" 

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("http://local.filmsobsession.com:8000")


@csrf_exempt
def login_redirect(request):
     
    params = dict()
    args = dict()
    args["client_id"] = FACEBOOK_APP_ID
    args["redirect_uri"] = REDIRECT_URL
    
    code = request.GET["code"]
    logger.debug("code: %s" % code)
    
    access_token_from_code = get_access_token_from_code(code, REDIRECT_URL, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
    logger.debug("access_token_from_code: %s" % access_token_from_code)
    
    access_token = access_token_from_code["access_token"]
    expires = access_token_from_code["expires"]
    
    logger.debug("access_token: %s" % access_token)
    logger.debug("expires: %s" % expires)
    
  
    
    user = auth.authenticate(token=access_token)
    logger.debug("user: %s" % user)
    
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
            pass
    else:
        # Return an 'invalid login' error message.
        pass
        
    
    return render_to_response('facebook-redirect.html', params, context_instance=RequestContext(request)) 
    
   
@csrf_exempt
def home(request):  
    try:
        signed_request = request.POST["signed_request"]
        parsed_request = parse_signed_request(signed_request, FACEBOOK_APP_SECRET)
        
        
        logger.debug("signed_request: %s" % signed_request)
        logger.debug("parsed_request: %s" % parsed_request)
        
        user = auth.authenticate(token=parsed_request["oauth_token"])
        logger.debug("user: %s" % user)
        
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                # Redirect to a success page.
            else:
                # Return a 'disabled account' error message
                pass
        else:
            # Return an 'invalid login' error message.
            pass

    except:
        pass

    
    args = dict()
    args["client_id"] = FACEBOOK_APP_ID
    args["redirect_uri"] = REDIRECT_URL
    
    params = dict()
    
    params["FACEBOOK_APP_ID"] = FACEBOOK_APP_ID
    params["FACEBOOK_APP_SECRET"] = FACEBOOK_APP_SECRET
    params["REDIRECT_URL"] = REDIRECT_URL

    
    args["display"] = "popup"
    args["response_type"] = "code"
    args["scope"] = "email"
    
    
    params["redirect2"] = auth_url(FACEBOOK_APP_ID, REDIRECT_URL, ["email"], "display")
    
    
    
    #args["fbconnect"] = "1"

    #return HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))
    params["redirect"] = "https://www.facebook.com/dialog/oauth?" + urllib.urlencode(args)
    #return HttpResponseRedirect("https://www.facebook.com/dialog/oauth?" + urllib.urlencode(args))
    
    
    return render_to_response('home.html', params, context_instance=RequestContext(request))

        
    
        
        
        
        
        
        
        
    
    