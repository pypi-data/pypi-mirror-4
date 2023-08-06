from django.contrib import auth
import logging
from facebook import parse_signed_request
from django.conf import settings



logger = logging.getLogger(__name__)



def facebook_canvas_index(a_view):
    """
    Make another a function more beautiful.
    """
    def _decorated(*args, **kwargs):
        print "Cargando decorador 'facebook_canvas_index'"
        request = args[0]   
        
        try:
            signed_request = request.POST["signed_request"]
            parsed_request = parse_signed_request(signed_request, settings.FACEBOOK_APP_SECRET)
            
            #logger.debug("signed_request: %s" % signed_request)
            #logger.debug("parsed_request: %s" % parsed_request)
            
            user = auth.authenticate(token=parsed_request["oauth_token"])
            #logger.debug("user: %s" % user)
            
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
        
        return a_view(*args, **kwargs)
    
    
    return _decorated