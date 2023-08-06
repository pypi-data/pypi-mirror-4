# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from models import UserProfile

import logging
import facebook

logger = logging.getLogger(__name__)

class FacebookBackend:
    
    """
        Autentificacion basada en un token
    """
    def authenticate(self, token=None):        
        
        graph = facebook.GraphAPI(token)
    
        profile = graph.get_object("me")
        logger.debug(profile)
        uid = profile["id"]
           
        """
            El nombre de nuestro usuario sera el id de facebook
            No seria mejor tener un UserProfile para facebook que aniadiese un fb_id
            y rellenase los campos mejor
        """
        
        
        try:
            userProfile = UserProfile.objects.get(uid=uid)
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
            logger.debug("-NO- Encontrado userProfile: %s" % user)
            return user
            

    
        """
            Esto no haria falta hacerlo cada vez,no?
            Solo cuando se crea el usuario
        """
        
        """
        user.set_unusable_password()
        user.email = profile['email']
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.save()
        """
        
        
        
        """
            En esta parte hemos creado el usuario en nuestro sistema si no existia
            o bien hemos conseguido el usuario de nuestro sistema si existtia
        """

        """
            Borramos la session?
        """
        
        """
        try:
            FacebookSession.objects.get(uid=profile['id']).delete()
        except FacebookSession.DoesNotExist, e:
            pass

        facebook_session.uid = profile['id']
        facebook_session.user = user
        facebook_session.save()
        """

        return user
   
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        