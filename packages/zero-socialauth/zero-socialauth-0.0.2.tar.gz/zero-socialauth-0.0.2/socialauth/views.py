# -*- coding: utf-8 -*-
import urllib

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django.contrib.auth import login


current_site = Site.objects.get_current()

FACEBOOK_APP_ID = getattr(settings, 'FACEBOOK_APP_ID', '')
FACEBOOK_SECRET_KEY = getattr(settings, 'FACEBOOK_SECRET_KEY', '')
FACEBOOK_SCOPE = getattr(settings, 'FACEBOOK_SCOPE',"email,publish_stream")


def del_dict_key(src_dict, key):
    if key in src_dict:
        del src_dict[key]


def facebook_login(request):
    """
    Vista para identificarse usando facebook.
    """
    next = request.GET.get('next', None)
    if next:
        request.session['facebook_login_next'] = next

    redirect_uri = 'http://www.%s%s' % (current_site.domain, reverse("socialauth_done"))

    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": redirect_uri,
        "scope": FACEBOOK_SCOPE
    }

    url = "https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(params)

    return HttpResponseRedirect(url)


def facebook_login_done(request):
    """
    Procesa la respuesta de facebook.
    """

    user = authenticate(request=request)
    
    if not user:
        # Existio un error, redirigiendo a la página de login
        return HttpResponseRedirect(reverse('users_login'))
    
    login(request, user)
    
    next = request.GET.get('next')
    if not next and 'facebook_login_next' in request.session:
        next = request.session.pop('facebook_login_next')
    
    if next:
        return HttpResponseRedirect(next)
    
    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
