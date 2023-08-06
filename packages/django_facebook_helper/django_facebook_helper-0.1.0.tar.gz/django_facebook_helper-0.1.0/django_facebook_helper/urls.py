from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:    
    url(r'^auth-redirect/$', 'django_facebook_helper.views.login_redirect', name='facebook-auth-redirect'),
    url(r'^test/friends/$', 'django_facebook_helper.views.friends', name='facebook-test-friends'),
)
