# -*- coding: utf-8 -*-

from django import template


register = template.Library()
from django.conf import settings

"""
AMIGUITO  = u"1273360443" # Iñaki
LINK      = u"http://fo.dev.binomia.es/facebook/movies/detail/what-doesnt-kill-you/"
PICTURE   = u"http://fo.dev.binomia.es/media/images/movies/W/what_doesn_t_kill_you.jpg"
NAME      = u"What doesn't kill you?"
CAPTION   = u"filmsobsession.com"
DESC      = u"Dos amigos de los barrios bajos del sur de Boston se convierten en delincuentes de poca monta hasta que son contratados por un jefe mafioso que podría abrirles las puertas de un mundo mejor."
ACTION    = u"[{name: 'ver online', link: 'http://www.google.es'}]"

FACEBOOK_FEED_URL = "https://www.facebook.com/dialog/feed?app_id=%s&to=%s&actions=[{name:'%s',link:'%s'}]&link=%s&picture=%s&name=%s&caption=%s&description=%s&redirect_uri=%s&display=popup" % (
                        FACEBOOK_APP_ID, AMIGUITO, ACTION, LINK, PICTURE, NAME, CAPTION, DESC, FACEBOOK_REDIRECT_URL)

"""


@register.simple_tag(takes_context=True)
def facebook_feed_url(context, friend, link, picture, name, caption, description, action_name, action_link):
    
    request = context['request']
    
    faceboo_app_id = settings.FACEBOOK_APP_ID
    
    return "https://www.facebook.com/dialog/feed?app_id=%s&to=%s&actions=[{name:'%s',link:'%s'}]&link=%s&picture=%s&name=%s&caption=%s&description=%s&redirect_uri=%s&display=popup" % (
                        faceboo_app_id, friend, action_name, action_link, link, picture, name, caption, description, ".")

