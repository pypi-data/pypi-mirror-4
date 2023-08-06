# Create your views here.

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

from django.conf import settings
from django.contrib import auth


from facebook import get_access_token_from_code, GraphAPI

import logging
from django_facebook_helper.forms import WallPostForm
logger = logging.getLogger(__name__)



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
    try:
        code = request.GET["code"]
        access_token_from_code = get_access_token_from_code(code, settings.FACEBOOK_REDIRECT_URL, settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)
        
        access_token = access_token_from_code["access_token"]
        expires = access_token_from_code["expires"]
        
        logger.debug("access_token: %s" % access_token)
        logger.debug("expires: %s" % expires)
        
        user = auth.authenticate(token=access_token)
        logger.debug("user: %s" % user)
        
        if user is not None:
            if user.is_active:
                auth.login(request, user) # Redirect to a success page.
            else:
                pass # Return a 'disabled account' error message
        else:
            pass # Return an 'invalid login' error message.
    except:
        pass 
    
    return render_to_response('facebook-redirect.html', {}, context_instance=RequestContext(request)) 
         
   
def friends(request):
    access_token = request.user.profile.access_token
    logger.debug("access_token: %s" % access_token) 
    
    graph = GraphAPI(access_token = access_token)
    user_friends = graph.get_connections("me", "friends")

    logger.debug("friends: %s" % user_friends) 
    logger.debug("friends: %s" % user_friends["data"]) 

    return render_to_response('friends.html', {"friends" : user_friends["data"]}, context_instance=RequestContext(request))   
        
     
def wall_post(request):
    
    if request.method == 'POST': # If the form has been submitted...
        form = WallPostForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            message = form.cleaned_data['message']
            
            access_token = request.user.profile.access_token   
            logger.debug("access_token: %s" % access_token) 
            
            graph = GraphAPI(access_token = access_token)
            user_friends = graph.put_wall_post(message)
    
    
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = WallPostForm() # An unbound form

    
    return render_to_response('wall-post.html', {"form" : form}, context_instance=RequestContext(request))   
     
    
    
    
    
    
    
        
        
        
    
    