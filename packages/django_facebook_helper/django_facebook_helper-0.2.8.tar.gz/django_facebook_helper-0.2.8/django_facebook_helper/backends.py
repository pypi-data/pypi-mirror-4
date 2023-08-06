# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from models import UserProfile

import logging
import facebook

from django.utils.simplejson import JSONEncoder

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
        
        # Stores a json list of friends
        friends_json = None
        
        # try to get friends
        try:
            friends = graph.get_connections("me", "friends") 
            logger.debug(friends)
            
            friends_json = JSONEncoder().encode(friends["data"])
            logger.debug(friends_json)
            
        except Exception as e:
            logger.error(e)
            
      
        #Obtains fb user id.
        uid = profile["id"]
            
        try:
            # try to get a user based on fb uid stored in db.
            userProfile = UserProfile.objects.get(uid=uid)
            logger.debug("Encontrado userProfile: %s" % userProfile.user.username)
            
            #Update token
            userProfile.access_token = token
            
            if friends_json != None:
                logger.debug("friends to save: %s" % friends_json) 
                userProfile.friends = friends_json
            
            """
            TODO: falta por actualizar la fecha de expiración del token.
            """
            
            userProfile.save()
        
            
            return userProfile.user
        
        except UserProfile.DoesNotExist:
            logger.debug("UserProfile doesn't exists")
            
            try:
                logger.debug("Creating User.")       
                user = User()
                
                user, created = User.objects.get_or_create(
                                   username=uid, 
                                   defaults={
                                     'first_name': profile['first_name'],
                                     'last_name' : profile['last_name'],
                                     'email'     : profile['email'],
                                   })
                if created:
                    user.set_unusable_password()
                    user.save()
                    
                    
            except Exception as e:
                logger.error(e)
                return
                
              
            try:
                logger.debug("Creating UserProfile.")
                userProfile = UserProfile()
                userProfile.user = user;
                userProfile.access_token = token
                userProfile.uid = uid
                
                if friends_json != None:
                    logger.debug("friends to save: %s" % friends_json) 
                    userProfile.friends = friends_json
                    
                                  
                userProfile.save()
                logger.debug("Creado userProfile: %s" % user)
                
            except Exception as e:
                logger.error(e)
                
                
                
                
            return user
          
        # Never reached.  
        return user
   
   
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        