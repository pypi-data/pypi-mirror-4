from django.db import models
from django.contrib.auth.models import User
from django.utils.simplejson import JSONDecoder


import logging
logger = logging.getLogger(__name__)



class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    access_token = models.CharField(max_length=255, unique=True)
    expires = models.IntegerField(null=True)
    uid = models.BigIntegerField(unique=True, null=True)
    
    friends = models.TextField()

        
    class Meta:
        unique_together = ('user', 'uid')
        
    def __unicode__(self):
        return u'Session for %s (%s) ' % (self.user.username, self.user.email)
    
    def get_friends(self):
        """
        Gets a python structure contaning facebook friends.
        """
        try:
            return JSONDecoder().decode(self.friends)
        except:
            return None
            


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])