# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from models import UserProfile

import logging
import facebook

logger = logging.getLogger(__name__)

class FacebookBackend:
    
    """
        Token based authentication
    """
    def authenticate(self, token=None):        
        
        # Create an instance of facebook API centered in the user node.
        graph = facebook.GraphAPI(token)
    
        # Ask fb the user info.
        profile = graph.get_object("me")
        logger.debug(profile)
        
        #Obtains fb user id.
        uid = profile["id"]
            
        try:
            # try to get a user based on fb uid stored in db.
            userProfile = UserProfile.objects.get(uid=uid)
            
            #Update token
            userProfile.access_token = token
            
            """
            TODO: falta por actualizar la fecha de expiración del token.
            """
            
            userProfile.save()
        
            logger.debug("Encontrado userProfile: %s" % userProfile.user.username)
            return userProfile.user
        
        except UserProfile.DoesNotExist:
            user = User()
            user.set_unusable_password()
            user.email = profile['email']
            user.username = uid
            user.first_name = profile['first_name']
            user.last_name = profile['last_name']
            user.save()
            
            
            userProfile = UserProfile()
            userProfile.user = user;
            userProfile.access_token = token
            userProfile.uid = profile["id"]
            
            userProfile.save()
            logger.debug("Creado userProfile: %s" % user)
            return user
          
        # Never reached.  
        return user
   
   
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        